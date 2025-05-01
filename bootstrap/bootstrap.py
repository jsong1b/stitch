#!/usr/bin/env python3


# a simple python script to bootstrap Stitch
# will be replaced later with an old version of the actual Stitch script
# very bad error handling cuz this is just temporary


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

    # append blocks to each other
    for block in blocks:
        if block.append_to == None:
            continue
        append_block(block, blocks)

    # expand named references in `<<<>>>`
    # also write to output file
    for block in blocks:
        if block.export_to == None:
            continue
        expand_refs(block, blocks)

        with open(block.export_to, 'w') as file:
            for line in block.contents:
                file.write(line + '\n')


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

        if re.match(r"^.*\+.+$", cur_block.name):
            if len(cur_block.name.split('+')) != 2:
                cur_block.name = ""
                cur_block.append_to = cur_block.name[1:]
            else:
                (cur_block.name, cur_block.append_to) = cur_block.name.split(
                    '+'
                )
        state = "block named"

    return (None, blocks)


def append_block(block, blocks):
    append_block_name = block.append_to
    append_block_file = block.file
    if re.match(r'^.+@.+$', block.append_to):
        (append_block_name, append_block_file) = block.append_to.split('@')

    for i, b in enumerate(blocks):
        if append_block_name != b.name or append_block_file != b.file:
            continue

        blocks[i].contents += block.contents


def expand_refs(block, blocks):
    new_contents = []
    lines = block.contents.copy()
    for line in lines:
        if not re.match('^.*<<<.+>>>.*$', line):
            new_contents += [line]
            continue

        prefix = line.split('<<<')[0]
        suffix = line.split('>>>')[1]

        ref_name = re.findall(r'<<<.+>>>', line)[0][3:-3]
        ref_file = block.file
        if re.match(r'^.+@.+$', ref_name):
            (ref_name, ref_file) = ref_name.split('@')

        for b in blocks:
            if ref_name != b.name or ref_file != b.file:
                continue

            expand_refs(b, blocks)
            for ref_line in b.contents:
                if ref_line == "":
                    new_contents += [""]
                    continue

                new_contents += [prefix + ref_line + suffix]

    block.contents = new_contents


if __name__ == "__main__":
    main()
