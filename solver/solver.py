"""
solver.py

Run `artifact` from /chunk with input.txt test cases and compare results against expected output.

Expect contents of /chunk:
artifact -> an executable file (shebang can be configured for interpreted languages) to be run
input.txt -> private test input
output.txt -> expected output
"""

import subprocess
import logging
import sys
import json
import time
import psutil

logging.basicConfig(level=logging.DEBUG)

def main(timeout, memory_limit) -> int:
    results = {}

    timeout = int(timeout) * 1000
    if timeout == 0: timeout = int(10e10)   #max 10 seconds in ns
    memory_limit = int(memory_limit)
    process = psutil.Process()

    with open("/chunk/tests.txt", "r") as tfp:
        tests = json.load(fp=tfp)
        for i, in_line, expected_out in tests:
            try:
                result = subprocess.Popen("/chunk/artifact", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                start_time = time.time_ns()
                
                while result.poll() is None:
                    # Check memory usage
                    mem_usage = process.memory_info().rss
                    if memory_limit != 0 and mem_usage > memory_limit:
                        result.terminate()
                        logging.warning(f"Test {i} terminated due to excessive memory usage: {mem_usage} bytes")
                        results[i] = "memfail"
                        break
                    
                    # Check timeout
                    if time.time_ns() - start_time > timeout:
                        result.terminate()
                        logging.warning(f"Test {i} terminated due to timeout")
                        results[i] = "timeout"
                        break
                    
                    time.sleep(0.1)

                produced_output, _ = result.communicate()
                produced_output = produced_output.decode()
                if produced_output == expected_out:
                    logging.info(f"Test {i} passed")
                    results[i] = "passed"
                else:
                    logging.warning(f"Test {i} not passed. Expected {expected_out} but got {produced_output}")
                    results[i] = "failed"
            
            except Exception as e:
                logging.error(f"Test case {i} terminated due to error {str(e)}")
                results[i] = "error"

    print(json.dumps(results))

if __name__ == "__main__":
    main(*sys.argv[1:3])