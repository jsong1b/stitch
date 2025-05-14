# Pandoc Frontend

This is a frontend for `Stitch` utilizing [Pandoc](https://pandoc.org) to parse
documents and extract blocks into the [JSON IR Spec](./json_spec.md).

[stitch-pandoc.py](./stitch-pandoc.py):
```python
#!/usr/bin/env python3


<<<Imports>>>


def main():
    <<<Main Function>>>


<<<Functions>>>


if __name__ == "__main__":
    main()
```

## Check for Pandoc

Pandoc *MUST* be installed for this script to work.

`+Imports`:
```python
import shutil
import sys
```

`+Main Function`:
```python
if shutil.which("pandoc") == None:
    print(
        "\033[31mPandoc Stitch Frontend: Error: pandoc not found\033[0m",
        file = sys.stderr
    )
    sys.exit(1)
```

## Parse CLI Arguments

`+Main Function`:
```python
only_check_for_files = False
cur_from_type = "auto"
files = []

args = iter(sys.argv[1:]) # in order to avoid annoying double continue logic

for i, arg in enumerate(args):
    if only_check_for_files == False:
        <<<Parse CLI Flags>>>

    <<<Check Files>>>
```

### Flags

The `-f/--from` flag tells Pandoc the doctype of the input. It is used just
like in Pandoc, for example `-f markdown`. This is useful for specifying a
certain type of markup. All the files after this flag will be passed into
Pandoc with the doctype, and the flag can be repeated multiple times. By
default, if this flag is not passed, the `auto` type is assigned to all files,
which means Pandoc will automatically determine the filetype. You can also
manually pass `auto` into the flag for this behaviour.

`+Parse CLI Flags`:
```python
if arg in ["-f", "--from"]:
    if i >= len(sys.argv[1:]) - 1:
        print(
            f"\033[33mPandoc Stitch Frontend: Warning: \"{arg}\" passed at position {i + 1} with no filetype",
            file = sys.stderr
        )
        print("Ignoring last argument...\033[0m", file = sys.stderr)
        continue

    cur_from_type = sys.argv[i + 1]
    next(args, None) # this avoids annoying double continue logic
    continue
```

Everything after `--` is considered a file. This is common CLI tool behaviour.

`+Parse CLI Flags`:
```python
if arg == "--":
    only_check_for_files = True
    continue
```

### Files

Each file is checked for their existance and 

This requires the `os` module.

`+Imports`:
```python
import os
```

We save the absolute path of the file to make the output JSON more reliable.

`Check Files`:
```python
if not (os.path.isfile(arg) and os.access(arg, os.R_OK)):
    print(
        f"\033[33mPandoc Stitch Frontend: Warning: File \"{arg}\" does not exist or is not readable",
        file = sys.stderr
    )
    print(
        f"Skipping file \"{arg}\"...\033[0m",
        file = sys.stderr
    )
    continue

files += [(cur_from_type, os.path.abspath(arg))]
```

If no valid files are passed into the script, then an error should be output
to the user.

`+Main Function`:
```python
if len(files) <= 0:
    print(
        "\033[31mPandoc Stitch Frontend: Error: No valid files passed into script\033[0m",
        file = sys.stderr
    )
    sys.exit(1)
```

## Get Pandoc Output

`+Imports`:
```python
import json
```

`+Main Function`:
```python
blocks = []
for file in files:
    unfiltered_blocks = {}
    output = ""

    try:
        if file[0] == "auto":
            output = os.popen(f"pandoc {file[1]} -t json").read()
        else:
            output = os.popen(f"pandoc -f {file[0]} {file[1]} -t json").read()

        unfiltered_blocks = json.loads(output)['blocks']
    except Exception as e:
        print(
            f"\033[33mPandoc Stitch Frontend: Warning: Could not run Pandoc on file \"{file[1]}\": {str(e)}",
            file = sys.stderr
        )
        print(f"Skipping file \"{file[1]}\"...\033[0m", file = sys.stderr)
        continue

    blocks += extract_blocks(file[1], unfiltered_blocks)

print(json.dumps({"blocks": blocks}), file = sys.stdout)
```

Blocks need to be extracted recursively in order to properly walk the Pandoc's
AST.

`+Functions`:
```python
def extract_blocks(file, pandoc_blocks):
    saved_blocks = []
    block_metadata = None

    for block in pandoc_blocks:
        if type(block) == list:
            saved_blocks += extract_blocks(file, block)
        elif type(block) == dict:
            if "t" not in block:
                continue

            if block_metadata != None:
                <<<Save Code Block>>>

            # if block["t"] == "Para":
            <<<Extract Block Metadata>>>

            for key, val in block.items():
                if type(val) == list:
                    saved_blocks += extract_blocks(file, val)

    return saved_blocks
```

Blocks recognized by Stitch will be formatted as either a link or code text
followed by a `:` then an actual code block. Code blocks are only searched for
after its metadata is found.

`Extract Block Metadata`:
```python
if not ((type(block) == dict and "c" in block and len(block["c"]) >= 2)
    and (block["c"][1] == {"t": "Str", "c": ":"})
    and (type(block["c"][0]) == dict)
    and (block["c"][0]["t"] in ["Code", "Link"])):
    continue

block_metadata = block["c"][0]
continue
```

### Saving the Code Block

It has to be ensured that the current block is of the type `CodeBlock`. This is
because this is a check that happens immediately after a block's metadata is
found, so if the current block is not of type `CodeBlock`, the metadata should
be assumed to not be associated with anything and will be ignored.

`Save Code Block`:
```python
if block["t"] != "CodeBlock":
    block_metadata = None
    continue

invalid_block = False
```

Here are all of the keys used as specified by the [JSON IR](./json_spec.md).

`+Save Code Block`:
```python
saved_block = {
    "lines":          block["c"][1].split("\n"),
    "from":           file,
    "export":         "",
    "name":           "",
    "append":         "",
    "append_to_from": "",
}
```

The metadata contains information about the block that is needed for the JSON.

`+Save Code Block`:
```python
if block_metadata["t"] == "Link":
    saved_block["export"] = block_metadata["c"][2][0]

    for elem in block_metadata["c"][1]:
        if elem["t"] not in ["Str", "Space"]:
            invalid_block = True
            break

        if elem["t"] == "Space":
            saved_block["name"] += " "
        else:
            saved_block["name"] += elem["c"]
else:
    saved_block["name"] = block_metadata["c"][1]
```

The data needs some extra processing in order to produce the correct JSON.

`+Save Code Block`:
```python
if "+" in saved_block["name"]:
    if len(saved_block["name"].split("+")) > 2:
        invalid_block = True

    (
        saved_block["name"],
        saved_block["append"]
    ) = saved_block["name"].split("+")

if "@" in saved_block["append"]:
    if len(saved_block["append"].split("@")) > 2:
        invalid_block = True

    (
        saved_block["append"], 
        saved_block["append_to_from"]
    ) = saved_block["append"].split("@")

if saved_block["export"] != "":
    if saved_block["name"] == "":
        saved_block["name"] == block_metadata["c"][2][0]

    saved_block["export"] = os.path.normpath(
        os.path.join(
            os.path.dirname(file),
            block_metadata["c"][2][0]
        )
    )
```

Ensure only blocks with the correct format are turned into JSON.

`+Save Code Block`:
```python
if invalid_block == True:
    block_metadata = None
    continue
```

Certain keys in the table can be removed if they are empty.

`+Save Code Block`:
```python
cleaned_block = {}
for key, val in saved_block.items():
    if (type(val) == str and val == "" and
        key in ["export", "name", "append", "append_to_from"]):
        continue
    cleaned_block[key] = val

saved_blocks += [cleaned_block]
```

If `block_metadata` is not reset, then only the first block in a series of
blocks will be extracted.

`+Save Code Block`:
```python
block_metadata = None
```
