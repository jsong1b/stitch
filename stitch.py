#!/usr/bin/env python3


import sys
import json


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




if __name__ == "__main__":
    main()
