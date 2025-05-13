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

for i, arg in enumerate(sys.argv[1:]):
    if only_check_for_files == False:
        <<<Parse CLI Flags>>>
```

### Flags

The `-f/--from` flag tells Pandoc the filetype of the input. It is used just
like in Pandoc, for example `-f markdown`. This is useful for specifying a
certain type of markup. All the files after this flag will be passed into
Pandoc with the filetype, and the flag can be repeated multiple times. By
default, if this flag is not passed, the `auto` type is assigned to all files,
which means Pandoc will automatically determine the filetype. You can also
manually pass `auto` into the flag for this behaviour.

`+Parse CLI Flags`:
```python
if arg in ["-f", "--from"]:
    if i >= len(sys.argv[1:]) - 1:
        print(
            f"\033[31mPandoc Stitch Frontend: Warning: \"{arg}\" passed at position {i + 1} with no filetype",
            file = sys.stderr
        )
        print("Ignoring last argument...\033[0m", file = sys.stderr)
        continue

    cur_from_type = arg
    continue
```

Everything after `--` is considered a file. This is common CLI tool behaviour.

`+Parse CLI Flags`:
```python
if arg == "--":
    cur_from_type = True
    continue
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
