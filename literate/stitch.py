#!/usr/bin/env python3


import sys
import json


def main():
    json_input = []
    check_only_for_files = False
    for arg in sys.argv[1:]:
        try:
            with open(arg) as file:
                json_input += [json.load(file)]
        except Exception as e:
            print(
                f"\033[33mStitch: Error reading file \"{arg}\" as JSON: {str(e)}",
                file = sys.stderr
            )
            print(f"Stitch: Skipping {arg}...\033[0m", file = sys.stderr)
    if not sys.stdin.isatty():
        stdin_lines = "".join(sys.stdin)
        try:
            json_input += [json.loads(stdin_lines)]
        except Exception as e:
            print(
                f"\033[33mStitch: Error reading stdin as JSON: {str(e)}",
                file = sys.stderr
            )
            print("Stitch: Skipping stdin...\033[0m", file = sys.stderr)




if __name__ == "__main__":
    main()
