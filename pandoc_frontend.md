# Pandoc Frontend

This is a frontend for `Stitch` utilizing [Pandoc](https://pandoc.org) to parse
documents and extract blocks into the [JSON IR Spec](./json_spec.md).

[stitch-pandoc.py](stitch-pandoc.py):
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

## TODO: Implement Creating New Blocks When Appending to Non-existant Ones

`Imports`:
```python
```

`Main Function`:
```python
```

`Functions`:
```python
```

`Parse CLI Flags`:
```python
```
