from django.test import TestCase
from .tasks import test_chain, engine
from celery.result import AsyncResult
import base64
import os
import random

class TestBuild(TestCase):
    def setUp(self):
        self.uid = str(random.randint(1000, 200000))
        while os.path.exists(os.path.join(engine.workingdir, self.uid)):
            self.uid = str(random.randint(1000, 200000))

    @staticmethod
    def valid_c_source():
        src = """#include <stdio.h>
    int main() {
        printf("hello world");
        return 0;
    }
    """
        return base64.b64encode(src.encode()).decode()
    
    def test_complete_chain(self):
        checktests = [(0, "input", "hello world")]
        chain_res = test_chain("c", self.valid_c_source(), self.uid, checktests)
        
        chain_res.get(timeout=10)

        self.assertNotEqual(chain_res.id, 0)
        self.assertTrue(chain_res.successful())
    
    @staticmethod
    def invalid_c_source():
        src = """#include <stdio.h>
    int main() {
        printf("hello world";
        return 0;
    }
    """
        return base64.b64encode(src.encode()).decode()

    def test_complete_chain_compiletime_error(self):
        checktests = [(0, "input", "hello world")]
        chain_res = test_chain("c", self.invalid_c_source(), self.uid, checktests)

        chain_res.get(timeout=10)

        self.assertNotEqual(chain_res.id, 0)
        self.assertTrue(chain_res.failed())
