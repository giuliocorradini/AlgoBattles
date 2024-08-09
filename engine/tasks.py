from celery import shared_task, chain
from .engine import Engine

engine = Engine()

@shared_task
def build(language, source, uid):
    engine.compile(language, source, uid)

@shared_task
def test(chunk, uid):
    engine.test(chunk, uid)

def test_chain(language, source, uid):
    """Build and tests the provided call by running
    the build and test tasks in a chain"""
    res = build.apply_async((language, source, uid), link=test.s(uid=uid))
    #print(res.get())