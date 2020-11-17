# filediff
Tool to test output produced by ml

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
```
def my_test:
    out_file = <path to my output file>
    with file_diff(out_file, do_raise=True):
        code_that_generates_an_output_file(..., output_path=out_file)
```


## Example
```python
from file_diff import file_diff
import json

def test_stuff():
    output_path = "reference_path.json"
    with file_diff(output_path, tolerance=0.0000001):
        out = do_something()
        with open(output_path, "w") as fp:
            fp.write(json.dumps(out))

```
