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

[JSON Test](tests/test2.json):
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
    "from": "./test2.json",
    "export": "/tmp/test1.txt",
    "name": "/tmp/test1.txt",
    "lines": [
        "Hello, world!"
    ]
},
```

The `export` key tells `Stitch` the file to write `lines` to. The path of the
file in `export` should be some absolute path, determined by the frontend based
on the source document. The `from` key tells `Stitch` where a block comes from,
which is necessary when determining how to string blocks together.

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
json_blocks = []
```

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
            json_blocks += json.load(file)["blocks"]
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
        json_blocks += json.loads(stdin_lines)["blocks"]
    except Exception as e:
        print(
            f"\033[33mStitch: Error reading stdin as JSON: {str(e)}",
            file = sys.stderr
        )
        print("Stitch: Skipping stdin...\033[0m", file = sys.stderr)
```

### Validating the JSON

All of the JSON blocks should have the `lines` key, and a warning should be
given to the user if otherwise. Additionaly, there should be at least 1 valid
block provided to `Stitch`, otherwise the program should error to notify the
user.

`+Main Function`:
```python
tmp_json_blocks = []
for block in json_blocks:
    if "lines" not in block:
        print(
            f"\033[33mStitch: Block {block} has no key \"lines\"",
            file = sys.stderr
        )
        print("Skipping block...\033[0m")
        continue
    tmp_json_blocks += [block]

json_blocks = tmp_json_blocks
if len(json_blocks) < 1:
    print(f"\033[31mStitch: No valid blocks found\033[0m", file = sys.stderr)
    sys.exit(1)
```

## Appending Blocks

Blocks can be appended to each other, which is useful if you want to make a
complete source file without having to put everything in one big source code
block.

The value of the `append` key must be the value of the `name` key of another
block. Additionally, the `append_to_from` key can be specified in order to
tell `Stitch` that the block to append to is from a different file.

### Append Function

`+Functions`:
```python
def append_block(block, blocks):
    if "append" not in block:
        return "Append key not found"
    <<<Append Function>>>

    return None
```

These variables will be useful later when comparing the blocks in `blocks` to
check what we need to append to.

`+Append Function`:
```python
append_name = block["append"]
append_from = block["from"]
if "append_to_from" in block:
    append_from = block["append_to_from"]
```

There is most likely a block in `blocks` that matches the value in `append`.

`+Append Function`:
```python
block_found = False
for b in blocks:
    if append_from != b["from"]:
        continue

    b_name = ""
    if "name" in b:
        b_name = b["name"]
    elif "export" in b:
        b_name = b["export"]

    if append_name == b_name:
        b["lines"] += block["lines"]
        block_found = True
        return None
```

If there the block to append to is not found in `blocks`, a new block should be
appended to the list.

`+Append Function`:
```python
blocks += [{
    "name": append_name,
    "from": append_from,
    "lines": block["lines"]
}]
```

### Calling the Function

`+Main Function`:
```python
for block in json_blocks:
    if "append" in block:
        err = append_block(block, json_blocks)
        if err != None:
            print(
                f"\033[;33mStitch: error appending block: {err}\033[;0m",
                file = sys.stderr
            )
```

## Expanding References

Blocks can include references to other blocks using `<<<>>>` delimiters. Inside
should be the name of the block and optionally `@{from}` to specify where the
block comes from. If no such distinction is made, the referenced block is
assumed to be from the same file as the block referencing it.

`+Test JSON Blocks`:
```json
{
    "export": "/tmp/test3.txt",
    "name": "/tmp/test3.txt",
    "from": "./test2.json",
    "lines": [
        "This is a block that references another block.",
        "<<<Test Named Block 1>>>"
    ]
},
{
    "name": "Test Named Block 1",
    "from": "./test2.json",
    "lines": [
        "This will be appended to blocks that reference `Test Named Block 1`"
    ]
},
```

This would result in a file `/tmp/test3.txt` with the output:

```txt
This is a block that references another block.
This will be appended to blocks that reference `Test Named Block 1`
```

### Expand Function

`+Functions`:
```python
def expand_refs(block, blocks, visited_blocks = []):
    <<<Block Already Checked>>>

    contents = []
    for line in block["lines"]:
        <<<Expand Loop>>>

    return (None, contents)
```

#### Check for Reference

This is the part of `Stitch` that requries regex, so we have to import the
`re` module. Regex will be used to check how

`+Imports`:
```python
import re
```

We need regex to find lines that include the pattern `<<<.+>>>`, which is a
line containing a reference.

`+Expand Loop`:
```python
if not re.match("^.*<<<.+>>>.*$", line):
    contents += [line]
    continue

if len(re.findall("<<<.+>>>", line)) != 1:
    return ("", None)

ref_name = re.findall("<<<.+>>>", line)[0][3:-3]
ref_from = block["from"]
if "@" in ref_name:
    (ref_name, ref_from) = ref_name.split("@")
```

#### Prefixes and Suffixes

The text before and after a reference should be copied to every line inside the
reference, mainly to keep indentation levels and comments. For example:

`+Test JSON Blocks`:
```json
{
    "export": "/tmp/test4.txt",
    "name": "/tmp/test4.txt",
    "from": "./test2.json",
    "lines": [
        "prefix: <<<Test Named Block 2>>>",
        "<<<Test Named Block 2>>> :suffix",
        "prefix: <<<Test Named Block 2>>> :suffix"
    ]
},
{
    "name": "Test Named Block 2",
    "from": "./test2.json",
    "lines": [
        "This block will have prefixes and suffixes prepended / appended."
    ]
}
```

Will output:

```txt
prefix: This block will have prefixes and suffixes prepended / appended.
This block will have prefixes and suffixes prepended / appended. :suffix
prefix: This block will have prefixes and suffixes prepended / appended. :suffix
```

If there are no prefix or suffix, none will be prepended / appended.

`+Expand Loop`:
```python
(prefix, suffix) = ("", "")
if len(line.split("<<<")) == 2:
    prefix = line.split("<<<")[0]
if len(line.split(">>>")) == 2:
    suffix = line.split(">>>")[1]
```

#### Expand the Reference

The referenced block is most likely in `blocks`.

`+Expand Loop`:
```python
reference_found = True
for b in blocks:
    if ("name" not in b
        or ref_name != b["name"]
        or ref_from != b["from"]):
        continue

    <<<Reference Found>>>
```

The contents should be expanded recursively so that *all* references are
expanded. Otherwise, if a block is referenced but also contains references to
another block, that reference will not be expanded.

`+Reference Found`:
```python
(err, b["lines"]) = expand_refs(b, blocks, visited_blocks + [block])
if err != None:
    if err == "Self-referential expansion":
        return (err, block["lines"])
    else:
        return (err, None)
```

There is a chance this creates an infinite recursive loop, in which case the
function should abort and simply return the original content with an error.

`Block Already Checked`:
```python
for b in visited_blocks:
    if (("name" in b and "name" in block and block["name"] == b["name"])
        or ("export" in b and "export" in block
            and block["export"] == b["export"])
        and block["from"] == b["from"]):
        return ("Self-referential expansion", None)
```

If the referenced block is not found, the line should just be left as is. This
is in case there is some source code that contains `<<<>>>` but is not
referring to another block.

`+Expand Loop`:
```python
if reference_found == False:
    contents += [line]
    continue
```

When 

`+Reference Found`:
```python
for l in b["lines"]:
    if l == "":
        contents += [""]
    else:
        contents += [prefix + l + suffix]
```

## Writing to Files

Only the files that are exported need to have their references expanded
initialially.

`+Main Function`:
```python
for block in json_blocks:
    if "export" in block:
        (err, lines) = expand_refs(block, json_blocks)
        if err != None:
            print(
                f"\033[33mStitch: Error expanding references in block: {block}: {err}\033[0m",
                file = sys.stderr
            )

        try:
            with open(block["export"], 'w') as file:
                for line in lines:
                    file.write(line + '\n')
        except Exception as e:
            print(
                f"\033[33mStitch: Error writing to file {block["export"]}: {e}",
                file = sys.stderr
            )
            print(f"Skipping {block["export"]}...\033[0m", file = sys.stderr)
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

`Test JSON Blocks`:
```json
```

`Append Function`:
```python
```

`Expand Loop`:
```python
```

`Reference Found`:
```python
```
