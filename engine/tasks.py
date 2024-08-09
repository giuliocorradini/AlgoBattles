from celery import shared_task, chain
from .engine import Engine

engine = Engine()

@shared_task
def build(language, source, uid):
    return engine.compile(language, source, uid)

@shared_task
def test(chunk, uid, tests):
    return engine.test(chunk, uid, tests)

def test_chain(language, source, uid, tests):
    """Build and tests the provided call by running
    the build and test tasks in a chain"""

    res = build.apply_async((language, source, uid), link=test.s(uid, tests))
    #print(res.get())