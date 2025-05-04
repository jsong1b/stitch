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

## The JSON Format

Frontend programs to `Stitch` extract blocks from documents and place them in
JSON representation, either to be passed in through `stdin` or as a command
line argument.

[JSON Test 1](tests/test1.json):
```json
{
    "blocks": [
        <<<Test JSON Blocks>>>
    ]
}
```

The reason why a JSON representation is passed into `Stitch` is because there
are many markup formats that a document could be written in, so the only thing
that should be needed to write literate documents would be `Stitch` to handle
the backend and another program to translate the document into JSON.

### The Structure of a Block

Here is the most basic block that would produce a result:

`+Test JSON Blocks`:
```json
{
    "export": "/tmp/test1.txt",
    "lines": [
        "Hello, world!"
    ]
}
```

The `export` key tells `Stitch` the file to write `lines` to. The path of the
file in `export` should be some absolute path, determined by the frontend based
on the source document.

In this case, this will write to the file `/tmp/test1.txt`, putting in the
contents:

```txt
Hello, world!
```

More parts of the JSON representaion will be explained later in this document.

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
            json_input += json.load(file)["blocks"]
    except Exception as e:
        print(
            f"\033[33mStitch: Error reading file \"{arg}\" as JSON: {str(e)}",
            file = sys.stderr
        )
        print(f"Stitch: Skipping {arg}...\033[0m", file = sys.stderr)
```

### Read From `stdin`

This should be how `Stitch` will be mostly used, passing in the output of one
program to this.

`+Main Function`:
```python
if not sys.stdin.isatty():
    stdin_lines = "".join(sys.stdin)
    try:
        json_input += json.loads(stdin_lines)["blocks"]
    except Exception as e:
        print(
            f"\033[33mStitch: Error reading stdin as JSON: {str(e)}",
            file = sys.stderr
        )
        print("Stitch: Skipping stdin...\033[0m", file = sys.stderr)
```

## Appending Blocks

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

`Test JSON Blocks`:
```json
```
