from django.test import TestCase
from .tasks import test_chain
from .engine import Engine
from puzzle.models import Attempt
import base64
import os
import random
from time import sleep
from celery.exceptions import Ignore

class TestBuild(TestCase):
    def setUp(self):
        self.uid = str(random.randint(1000, 200000))
        while os.path.exists(os.path.join(Engine.get_instance().workingdir, self.uid)):
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
        chain_res = test_chain("c", self.valid_c_source(), self.uid, checktests, int(1e6), int(1e19))
        
        chain_res.get(timeout=2)

        self.assertNotEqual(chain_res.id, 0)
        self.assertTrue(chain_res.successful())

    @staticmethod
    def timeout_c_source():
        src = """
            #include <stdio.h>
            #include <unistd.h>
            int main() {
                sleep(10);
                return 0;
            }
        """
        return base64.b64encode(src.encode()).decode()
    
    def test_chain_timeout(self):
        checktests = [(0, "input", "hello world")]
        chain_res = test_chain("c", self.timeout_c_source(), self.uid, checktests, int(1), int(1e10))
        
        chain_res.get(timeout=2)
        solver_status, result = chain_res.result

        self.assertNotEqual(chain_res.id, 0)
        self.assertTrue(chain_res.successful())
        self.assertEqual(solver_status, "solver_success")
        self.assertEqual(result, '{"0": "timeout"}\n')

    def test_chain_memfail(self):
        checktests = [(0, "input", "hello world")]
        chain_res = test_chain("c", self.valid_c_source(), self.uid, checktests, int(1e6), int(1))
        
        chain_res.get(timeout=2)
        solver_status, result = chain_res.result

        self.assertNotEqual(chain_res.id, 0)
        self.assertTrue(chain_res.successful())
        self.assertEqual(solver_status, "solver_success")
        self.assertEqual(result, '{"0": "memfail"}\n')

