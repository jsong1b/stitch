#!/usr/bin/env python3


import shutil
import sys
import os


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




if __name__ == "__main__":
    main()
