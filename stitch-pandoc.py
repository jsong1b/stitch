#!/usr/bin/env python3


import shutil
import sys
import os
import json


def main():
    if shutil.which("pandoc") == None:
        print(
            "\033[31mPandoc Stitch Frontend: Error: pandoc not found\033[0m",
            file = sys.stderr
        )
        sys.exit(1)
    only_check_for_files = False
    cur_from_type = "auto"
    files = []

    args = iter(sys.argv[1:]) # in order to avoid annoying double continue logic

    for i, arg in enumerate(args):
        if only_check_for_files == False:
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
            if arg == "--":
                only_check_for_files = True
                continue

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
    if len(files) <= 0:
        print(
            "\033[31mPandoc Stitch Frontend: Error: No valid files passed into script\033[0m",
            file = sys.stderr
        )
        sys.exit(1)
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
                if block["t"] != "CodeBlock":
                    block_metadata = None
                    continue

                invalid_block = False
                saved_block = {
                    "lines":          block["c"][1].split("\n"),
                    "from":           file,
                    "export":         "",
                    "name":           "",
                    "append":         "",
                    "append_to_from": "",
                }
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
                if invalid_block == True:
                    block_metadata = None
                    continue
                cleaned_block = {}
                for key, val in saved_block.items():
                    if (type(val) == str and val == "" and
                        key in ["export", "name", "append", "append_to_from"]):
                        continue
                    cleaned_block[key] = val

                saved_blocks += [cleaned_block]
                block_metadata = None

            # if block["t"] == "Para":
            if not ((type(block) == dict and "c" in block and len(block["c"]) >= 2)
                and (block["c"][1] == {"t": "Str", "c": ":"})
                and (type(block["c"][0]) == dict)
                and (block["c"][0]["t"] in ["Code", "Link"])):
                continue

            block_metadata = block["c"][0]
            continue

            for key, val in block.items():
                if type(val) == list:
                    saved_blocks += extract_blocks(file, val)

    return saved_blocks


if __name__ == "__main__":
    main()
