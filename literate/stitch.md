# Stitch

This is the backend for `Stitch`. This program takes in a JSON representation
of a blocks it needs to tangle and writes to the correct files.

[Stitch Script](./stitch.py):
```python
#!/usr/bin/env python3


<<<Imports>>>


def main():
    <<<Main Function>>>


<<<Functions>>>


if __name__ == "__main__":
    main()
```

## The JSON Representation

Frontend programs to `Stitch` extract blocks from documents and place them in
JSON representation, either to be passed in through `stdin` or as a command
line argument.

[JSON Test 1](tests/test1.json):
```json
{
    "metadata": [
        {
            <<<Test JSON Metadata>>>
        }
    ],

    "settings": [
        {
            <<<Test JSON Settings>>>
        }
    ],

    "blocks": [
        {
            <<<Test JSON Blocks>>>
        }
    ]
}
```

## Parse CLI Arguments & `stdin`

The `sys` module allows us to access the CLI flags passed into the script as
well as `stdin`.

`+Imports`:
```python
import sys
```

We will store all of our JSON input into a list which will be iterated over to
find blocks / settings / metadata.

`+Main Function`:
```python
json_input = []
```

To convert the JSON into a dictionary for Python, we need to import the `json`
module.

`+Imports`:
```python
import json
```

### Read From CLI Arguments

Other than flags, the only thing that should be passed into `Stitch` are files
that contain the JSON representation.

`+Main Function`:
```python
check_only_for_files = False
for arg in sys.argv[1:]:
    try:
        with open(arg) as file:
            json_input += [json.load(file)]
    except Exception as e:
        print(
            f"\033[33mStitch: Error reading file \"{arg}\" as JSON: {str(e)}",
            file = sys.stderr
        )
        print(f"Stitch: Skipping {arg}...\033[0m", file = sys.stderr)
```

### Read From `stdin`

`+Main Function`:
```python
if not sys.stdin.isatty():
    stdin_lines = "".join(sys.stdin)
    try:
        json_input += [json.loads(stdin_lines)]
    except Exception as e:
        print(
            f"\033[33mStitch: Error reading stdin as JSON: {str(e)}",
            file = sys.stderr
        )
        print("Stitch: Skipping stdin...\033[0m", file = sys.stderr)
```

---

## TODO: Implement Creating New Blocks When Appending to Non-existant Ones

`Main Function`:
```python
```

`Imports`:
```python
```

`Functions`:
```python
```

`Test JSON Metadata`:
```json
```

`Test JSON Settings`:
```json
```

`Test JSON Blocks`:
```json
```
