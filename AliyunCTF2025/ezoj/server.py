import os
import subprocess
import uuid
import json
from flask import Flask, request, jsonify, send_file
from pathlib import Path

app = Flask(__name__)

SUBMISSIONS_PATH = Path("./submissions")
PROBLEMS_PATH = Path("./problems")

SUBMISSIONS_PATH.mkdir(parents=True, exist_ok=True)

CODE_TEMPLATE = """
import sys
import math
import collections
import queue
import heapq
import bisect

def audit_checker(event,args):
    if not event in ["import","time.sleep","builtins.input","builtins.input/result"]:
        raise RuntimeError

sys.addaudithook(audit_checker)


"""


class OJTimeLimitExceed(Exception):
    pass


class OJRuntimeError(Exception):
    pass


@app.route("/")
def index():
    return send_file("static/index.html")


@app.route("/source")
def source():
    return send_file("server.py")


@app.route("/api/problems")
def list_problems():
    problems_dir = PROBLEMS_PATH
    problems = []
    for problem in problems_dir.iterdir():
        problem_config_file = problem / "problem.json"
        print(problem_config_file)
        if not problem_config_file.exists():
            continue

        problem_config = json.load(problem_config_file.open("r"))
        print(problem_config)
        print(problem)
        problem = {
            "problem_id": problem.name,
            "name": problem_config["name"],
            "description": problem_config["description"],
        }
        problems.append(problem)

    problems = sorted(problems, key=lambda x: x["problem_id"])

    problems = {"problems": problems}
    return jsonify(problems), 200


@app.route("/api/submit", methods=["POST"])
def submit_code():
    try:
        data = request.get_json()
        code = data.get("code")
        problem_id = data.get("problem_id")

        if code is None or problem_id is None:
            return (
                jsonify({"status": "ER", "message": "Missing 'code' or 'problem_id'"}),
                400,
            )

        problem_id = str(int(problem_id))
        problem_dir = PROBLEMS_PATH / problem_id
        if not problem_dir.exists():
            return (
                jsonify(
                    {"status": "ER", "message": f"Problem ID {problem_id} not found!"}
                ),
                404,
            )

        code_filename = SUBMISSIONS_PATH / f"submission_{uuid.uuid4()}.py"
        with open(code_filename, "w") as code_file:
            code = CODE_TEMPLATE + code
            code_file.write(code)

        result = judge(code_filename, problem_dir)

        code_filename.unlink()

        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "ER", "message": str(e)}), 500


def judge(code_filename, problem_dir):
    test_files = sorted(problem_dir.glob("*.input"))
    total_tests = len(test_files)
    passed_tests = 0

    try:
        for test_file in test_files:
            input_file = test_file
            expected_output_file = problem_dir / f"{test_file.stem}.output"

            if not expected_output_file.exists():
                continue

            case_passed = run_code(code_filename, input_file, expected_output_file)
            print(case_passed)
            if case_passed:
                passed_tests += 1

        if passed_tests == total_tests:
            return {"status": "AC", "message": f"Accepted"}
        else:
            return {
                "status": "WA",
                "message": f"Wrang Answer: pass({passed_tests}/{total_tests})",
            }
    except OJRuntimeError as e:
        return {"status": "RE", "message": f"Runtime Error: ret={e.args[0]}"}
    except OJTimeLimitExceed:
        return {"status": "TLE", "message": "Time Limit Exceed"}


def run_code(code_filename, input_file, expected_output_file):
    with open(input_file, "r") as infile, open(
        expected_output_file, "r"
    ) as expected_output:
        expected_output_content = expected_output.read().strip()

        process = subprocess.Popen(
            ["python3", code_filename],
            stdin=infile,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = process.communicate(timeout=5)
            print(stdout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise OJTimeLimitExceed

        if process.returncode != 0:
            raise OJRuntimeError(process.returncode)

        if stdout.strip() == expected_output_content:
            return True
        else:
            return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
