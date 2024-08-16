from celery import shared_task
from celery.exceptions import Ignore
from .engine import Engine, CompileTimeError

engine = Engine()

@shared_task(bind=True)
def build(self, language, source, uid):
    try:
        return engine.compile(language, source, uid)
    except CompileTimeError as e:
        self.update_state(state="FAILURE", meta=e.logs)
        raise Ignore()

@shared_task
def test(chunk, uid, tests):
    return engine.test(chunk, uid, tests)

def test_chain(language, source, uid, tests):
    """Build and tests the provided call by running
    the build and test tasks in a chain.
    
    Returns the chain task ID. Can be used to retrieve the task result later on.
    """

    chain = build.si(language, source, uid) | test.s(uid, tests)
    return chain.apply_async()
