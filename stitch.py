#!/usr/bin/env python3


import sys
import json
import re


def main():
    json_blocks = []
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
    for block in json_blocks:
        if "append" in block:
            err = append_block(block, json_blocks)
            if err != None:
                print(
                    f"\033[;33mStitch: error appending block: {err}\033[;0m",
                    file = sys.stderr
                )
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


def append_block(block, blocks):
    if "append" not in block:
        return "Append key not found"
    append_name = block["append"]
    append_from = block["from"]
    if len(block["append"].split("@")) == 2:
        (append_name, append_from) = block["append"].split("@")
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
    blocks += [{
        "name": append_name,
        "from": append_from,
        "lines": block["lines"]
    }]

    return None
def expand_refs(block, blocks, visited_blocks = []):
    for b in visited_blocks:
        if (("name" in b and "name" in block and block["name"] == b["name"])
            or ("export" in b and "export" in block
                and block["export"] == b["export"])
            and block["from"] == b["from"]):
            return ("Self-referential expansion", None)

    contents = []
    for line in block["lines"]:
        if not re.match("^.*<<<.+>>>.*$", line):
            contents += [line]
            continue

        if len(re.findall("<<<.+>>>", line)) != 1:
            return ("", None)

        ref_name = re.findall("<<<.+>>>", line)[0][3:-3]
        ref_from = block["from"]
        if "@" in ref_name:
            (ref_name, ref_from) = ref_name.split("@")
        (prefix, suffix) = ("", "")
        if len(line.split("<<<")) == 2:
            prefix = line.split("<<<")[0]
        if len(line.split(">>>")) == 2:
            suffix = line.split(">>>")[1]
        reference_found = True
        for b in blocks:
            if ("name" not in b
                or ref_name != b["name"]
                or ref_from != b["from"]):
                continue

            (err, b["lines"]) = expand_refs(b, blocks, visited_blocks + [block])
            if err != None:
                if err == "Self-referential expansion":
                    return (err, block["lines"])
                else:
                    return (err, None)
            for l in b["lines"]:
                if l == "":
                    contents += [""]
                else:
                    contents += [prefix + l + suffix]
        if reference_found == False:
            contents += [line]
            continue

    return (None, contents)


if __name__ == "__main__":
    main()
