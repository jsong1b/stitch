#!/usr/bin/env python3


# a simple python script to bootstrap Stitch
# will be replaced later with an old version of the actual Stitch script


import os
import re
import sys


def main():
    lit_docs = []
    for arg in sys.argv[1:]:
        if not os.path.isfile(arg) or arg in lit_docs:
            continue
        lit_docs += [arg]

    blocks = []
    for doc in lit_docs:
        (err, new_blocks) = extract_blocks(doc)
        if err != None:
            # just some really basic error handling
            print(f"error opening file {doc}: {str(err)}")
            sys.exit(1)

        blocks += new_blocks

    for block in blocks:
        print("============================")
        print(block.name)
        print(block.file)
        print(block.append_to)
        print(block.export_to)
        print(block.contents)


class Block:
    def __init__(self, name, file, contents, append_to, export_to):
        self.name = name
        self.file = file
        self.contents = contents
        self.append_to = append_to
        self.export_to = export_to


def extract_blocks(file_path):
    lines = []
    try:
        with open(file_path, 'r') as file:
            lines = [line.rstrip() for line in file]
    except Exception as e:
        return(e, [])

    blocks = []
    cur_block = Block("", file_path, [], None, None)
    state = "not in block"
    for line in lines:
        if (state == "not in block" and
            not re.match(r"^((\[.+\]\(.+\))|(`.+`)):$", line)):
            # line not relevant to blocks
            continue

        if state == "block named":
            if line != "```":
                state = "in contents"
                continue

        if state == "in contents":
            if line != "```":
                cur_block.contents += [line]
                continue

            # end of block, append to `blocks`
            blocks += [cur_block]
            cur_block = Block("", file_path, [], None, None)
            state = "not in block"
            continue

        if re.match(r"^\[.+\]\(.+\):", line):
            cur_block.name = line.split("](")[0][1:]
            cur_block.export_to = line.split("](")[1][:-2]
        else:
            cur_block.name = line[1:-2]

        if re.match(r"^.+\+.+$", cur_block.name):
            (cur_block.name, cur_block.append_to) = cur_block.name.split('+')
        state = "block named"

    return (None, blocks)


if __name__ == "__main__":
    main()
