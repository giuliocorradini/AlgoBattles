from celery import shared_task
from celery.exceptions import Ignore
from celery.signals import task_postrun
from django.db import transaction
from django_celery_results.models import TaskResult
from puzzle.models import Attempt
from .engine import Engine, CompileTimeError
import json
import logging

@shared_task(bind=True)
def build(self, language, source, uid):
    engine = Engine.get_instance()

    try:
        return engine.compile(language, source, uid)
    except CompileTimeError as e:
        self.update_state(state="FAILURE", meta=e.logs)
        raise Ignore()

@shared_task
def test(chunk, uid, tests, timelimit, memlimit):
    engine = Engine.get_instance()
    return engine.test(chunk, uid, tests, timelimit, memlimit)

def test_chain(language, source, uid, tests, timelimit, memlimit):
    """Build and tests the provided call by running
    the build and test tasks in a chain.
    
    Returns the chain task ID. Can be used to retrieve the task result later on.
    """

    chain = build.si(language, source, uid) | test.s(uid, tests, timelimit, memlimit)
    return chain.apply_async()

@task_postrun.connect
def update_task_status(sender, task_id, task, args, kwargs, retval, state, **extra):
    if task == build and state == "IGNORED":
        uid = args[2]
        
        att = Attempt.objects.filter(pk=uid).first()
        if not att:
            return
        
        task_res = TaskResult.objects.filter(task_id=task_id).first()
        if not task_res:
            return
        
        with transaction.atomic():
            att.results = json.loads(task_res.result)
            att.build_error = True
            att.save()

    if task == test and state == "SUCCESS":
        with transaction.atomic():
            att = Attempt.objects.filter(task_id=task_id).first()
            if not att:
                return

            status, data = retval
            if status == "solver_success":
                results = json.loads(data)
                att.passed = all(map(lambda x: x == "passed", results.values()))
            else:
                att.build_error = True
                logging.warning(retval)

            att.results = data
            att.save()
