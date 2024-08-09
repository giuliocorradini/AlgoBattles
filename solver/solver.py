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

logging.basicConfig(level=logging.DEBUG)

def main(timeout) -> int:
    results = {}

    with open("/chunk/tests.txt", "r") as tfp:
        tests = json.load(fp=tfp)
        for i, in_line, expected_out in tests:
            try:
                result = subprocess.run("/chunk/artifact", input=in_line.encode(), capture_output=True, timeout=timeout)

                produced_output = result.stdout.decode()
                if produced_output == expected_out:
                    logging.info(f"Test {i} passed")
                    results[i] = "passed"
                else:
                    logging.warning(f"Test {i} not passed. Expected {expected_out} but got {produced_output}")
                    results[i] = "failed"
            
            except TimeoutError as te:
                logging.info(f"Signal timeout error for test case {i}")

    print(json.dumps(results)) 

if __name__ == "__main__":
    main(int(sys.argv[1]))