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
