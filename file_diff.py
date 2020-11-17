import inspect
import json
import os
import difflib
import filecmp
import shutil
import sys


class file_diff:
    """
    This function is inspired by vcrpy [https://vcrpy.readthedocs.io/en/latest/usage.html] but instead of saving an
    http session it saves a file the code under test generates.
    Copies the output file that your code under test is generating into a fixtures/<your_test_name>/filename if the
    fixture doesn't exist. This file is considered the reference fixture.
    If the reference fixture exists then it compares the current output file to the reference file and produces a diff.
    If the current output differs from the reference then it raises an exception
    You need to commit the reference file once it is generated and it looks good.
    If your reference needs to be updated just delete the file and run the test again so it produces a new reference.

    If tolerance is specified then the files are read as json and values are compared as floats

    Example usage:

    def my_test:
        out_file = <path to my output file>
        with file_diff(out_file, do_raise=True):
            code_that_generates_an_output_file(..., output_path=out_file)

    """
    def __init__(self, file_path, do_raise=True, tolerance=None):
        self.file_path = file_path
        self.caller_path = inspect.stack()[1].filename
        self.do_raise = do_raise
        self.tolerance = tolerance

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        filename = os.path.basename(self.file_path)
        caller_parts = self.caller_path.replace(".py", "").split("/")
        fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures", caller_parts[-2], caller_parts[-1])
        os.makedirs(fixture_dir, exist_ok=True)
        fixture_path = os.path.join(fixture_dir, filename)
        if os.path.isfile(fixture_path):
            # Fixture exists, do a diff
            if self.tolerance:
                self.diff_json(fixture_path, self.file_path)
            else:
                self.diff(fixture_path, self.file_path)
        else:
            # Create fixture if it doesn't exist
            shutil.copy(self.file_path, fixture_path)

    def diff(self, fixture_path, file_path):
        if not filecmp.cmp(fixture_path, file_path):
            # Files differ, write out a diff
            with open(fixture_path) as f:
                fixture_lines = f.readlines()
            with open(file_path) as f:
                file_lines = f.readlines()

            for line in difflib.context_diff(fixture_lines, file_lines, fromfile="reference", tofile="test_file"):
                sys.stdout.write(line)

            if self.do_raise:
                raise Exception("File contents have changed")

    def diff_json(self, fixture_path, file_path):
        if not filecmp.cmp(fixture_path, file_path):
            # Files differ, write out a diff
            with open(fixture_path) as f:
                content1 = json.load(f)
            with open(file_path) as f:
                content2 = json.load(f)

            if not self.compare(content1, content2) and self.do_raise:
                raise Exception("File contents have changed")

    def compare(self, example_json, target_json):
        if type(example_json) is list:
            if len(example_json) != len(target_json):
                print("Values changed: {}   ->   {}".format(example_json, target_json))
                return False
            for i in range(len(example_json)):
                if not self.compare(example_json[i], target_json[i]):
                    print("Values changed: {}   ->   {}".format(example_json[i], target_json[i]))
                    return False
        elif type(example_json) is dict:
            for x in example_json:
                if x not in target_json:
                    print("Values changed: {}   ->   {}".format(example_json, target_json))
                    return False
                if not example_json[x] == target_json[x]:
                    if not self.compare(example_json[x], target_json[x]):
                        print("Values changed: {}   ->   {}".format(example_json[x], target_json[x]))
                        return False
        else:
            try:
                if abs(float(example_json) - float(target_json)) > self.tolerance:
                    print("Values changed: {}   ->   {}".format(example_json, target_json))
                    return False
            except ValueError:
                # Can't convert to float
                pass

        return True

