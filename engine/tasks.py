from celery import shared_task
from .engine import Engine

engine = Engine()

@shared_task
def build(language, source, uid):
    engine.handle_build(language, source, uid)

@shared_task
def test(source, uid):
    engine.handle_test(source, uid)