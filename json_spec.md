# JSON Representation Specification

This document specifies the JSON representation passed into `Stitch`. An
intermediate representation is used when passing data to `Stitch` because I
want this to work with basically any document format without having to rewrite
the tangling part again. JSON is used because it is simple to use, there is a
builtin Python module for it, and it is widely used by other programs to pass
data around.

All the JSON really needs is a key called `blocks` that holds a list of the
blocks.

[Test JSON File](tests/test1.json):
```json
{
    "blocks": [
        <<<Blocks>>>
    ]
}
```

A block simply contains some keys specifying how `Stitch` should use the block.

The required keys are `lines`, `from`, and either `export` and `name` or
`append`.

The `lines` key should have the value of a list of strings that are the lines
of the block.

The `from` key should have the value of a string specifying the source file of
a block, which is useful in conjunction with the final 3 keys in how `Stitch`
puts blocks together or exports them. This can be either a relative or absolute
path. The format of this key is dependent on the frontend that generates the
JSON.

The other 3 keys need a bit more of an explanation.

## Exporting Blocks To Source Code (`export` Key)

The `export` key tells `Stitch` where to place the contents of a block. It's
value is a string of either the absolute or relative path of the output file.
In the case of an absolute path, `Stitch` will simply try to write to that
file. In the case of a relative path, `Stitch` will base the relative path
based on the directory of the file specified in the value of the `from` key.
Whether or not the path is absolute or relative is dependent on whatever
program generates the JSON or what the user specifies. Additionally, if no
other name is specified for a block, the value of `export` becomes the value
of `name`.

Here is an example using an absolute path:

`+Blocks`:
```json
{
    "lines": [
        "This line will be written to /tmp/absolute_export_test.txt."
    ],
    "from": "./some_document.md",
    "export": "/tmp/absolute_export_test.txt",
    "name": "/tmp/absolute_export_test.txt"
},
```

Which would output the following to `/tmp/absolute_export_test.txt`:

`/tmp/test.txt`:
```txt
This line will be written to /tmp/absolute_export_test.txt.
```

And here is an example using a relative path:

`+Blocks`:
```json
{
    "lines": [
        "This line will be written to ./relative_export_test.txt."
    ],
    "from": "./some_document.md",
    "export": "./relative_export_test.txt",
    "name": "./relative_export_test.txt"
}
```

Which would output the following to `./relative_export_test.txt`:

`./relative_export_test.txt`:
```txt
This line will be written to ./relative_export_test.txt.
```

This will be placed in the same directory as `./some_document.md`, so `.`.

## Appending Blocks to Each Other (`append` Key)

The `append` key tells `Stitch` what other block to add the contents of a block
to. It's value is the value of another block's `name`.

`+Blocks`:
```json
{
    "lines": [
        "This will export to ./append_test_same_file.txt and be appended to."
    ],
    "from": "./some_document.md",
    "export": "./append_test_same_file.txt",
    "name": "./append_test_same_file.txt"
},
{
    "lines": [
        "This is what is appended to ./append_test_same_file.txt."
    ],
    "from": "./some_document.md",
    "append": "./append_test_same_file.txt"
},
```

This will produce the following in `./append_test_same_file.txt`:

`./append_test_same_file.txt`:
```txt
This will export to ./append_test_same_file.txt and be appended to.
This is what is appended to ./append_test_same_file.txt.
```

Optionally, the `append_to_from` key can be provided if a block to be appended
and the block it needs to be appended to are from different files.

`+Blocks`:
```json
{
    "lines": [
        "This will export to ./append_test_different_file.txt.",
        "The block appended to this is from another file."
    ],
    "from": "./some_document.md",
    "export": "./append_test_different_file.txt",
    "name": "./append_test_different_file.txt"
},
{
    "lines": [
        "This is what is appended to ./append_test_different_file.txt.",
        "The block this is appended to is from another file."
    ],
    "from": "./some_other_document.md",
    "append": "./append_test_different_file.txt",
    "append_to_from": "./some_document.md"
},
```

`./append_test_different_file.txt`:
```txt
This will export to ./append_test_different_file.txt.
The block appended to this is from another file.
This is what is appended to ./append_test_different_file.txt.
The block this is appended to is from another file.
```

Notice how the second block's `from` key is `./some_other_document.md`, not
`./some_document.md` like the first block. This is why the `append_to_from` key
is needed to append the second block to the first block.

## Expanding References in Blocks (`name` Key)

The `name` key tells `Stitch` the name of the block. This is pretty
self-explanatory, and the key has been seen before in the previous sections of
this document. It is important to note that every block with an `import` key
also requires a `name` key, blocks with the `append` key do not require also
having a `name` key (they can still optionally have one).

Block names have another purpose, being used to insert the contents of a block
into another, kind of like C preprocessor macros. To reference another block,
place the value of the blocks `name` key between `<<<>>>`.

`+Blocks`:
```json
{
    "lines": [
        "This will export to ./reference_test_basic.txt.",
        "<<<Basic Reference Block>>>"
    ],
    "from": "./some_document.md",
    "export": "./reference_test_basic.txt",
    "name": "./reference_test_basic.txt"
},
{
    "lines": [
        "This block was referened by ./reference_test_basic.txt."
   ],
   "from": "./some_document.md",
   "name": "Basic Reference Block"
},
```

This produces the following in `./reference_test_basic.txt`:

`./reference_test_basic.txt`:
```json
This will export to ./reference_test_basic.txt.
This block was referened by ./reference_test_basic.txt.
```

If the reference (`<<<Block Name>>>`) has text before or after it, that text
will be copied to all the lines except empty ones.

`+Blocks`:
```json
{
    "lines": [
        "This will export to ./reference_test_fixes.txt.",
        "prefix: <<<Affixed Reference Block>>>",
        "<<<Affixed Reference Block>>> :suffix",
        "prefix: <<<Affixed Reference Block>>> :suffix",
    ],
    "from": "./some_document.md",
    "export": "./reference_test_fixes.txt",
    "name": "./reference_test_fixes.txt"
},
{
    "lines": [
        "This block has prefixes and suffixes.",
        "",
        "But not on empty lines."
   ],
   "from": "./some_document.md",
   "name": "Affixed Reference Block"
},
```

This will output the following to `./reference_test_fixes.txt`:

`./reference_test_fixes.txt`:
```json
This will export to ./reference_test_fixes.txt.
prefix: This block has prefixes and suffixes.

prefix: But not on empty lines.
This block has prefixes and suffixes. :suffix

But not on empty lines. :suffix
prefix: This block has prefixes and suffixes. :suffix

prefix: But not on empty lines. :suffix
```

If you want to expand a reference to a block from another file, use
`@From File` to what is in `<<<>>>`.

`+Blocks`:
```json
{
    "lines": [
        "This will export to ./reference_test_external.txt.",
        "<<<External Reference Block@./some_other_document.md>>>"
    ],
    "from": "./some_document.md",
    "export": "./reference_test_external.txt",
    "name": "./reference_test_external.txt"
},
{
    "lines": [
        "This block was referened by ./reference_test_external.txt.",
        "This block is from another file."
   ],
   "from": "./some_other_document.md",
   "name": "External Reference Block"
},
```

This will output the following to `./reference_test_external.txt`:

`./reference_test_external.txt`:
```txt
This will export to ./reference_test_external.txt.
This block was referened by ./reference_test_external.txt.
This block is from another file.
```

## TODO: Implement Creating New Blocks When Appending to Non-existant Ones

`Blocks`:
```json
```
