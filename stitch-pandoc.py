#!/usr/bin/env python3


import shutil
import sys


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

    for i, arg in enumerate(sys.argv[1:]):
        if only_check_for_files == False:
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
            if arg == "--":
                cur_from_type = True
                continue




if __name__ == "__main__":
    main()
