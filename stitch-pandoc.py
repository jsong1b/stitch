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




if __name__ == "__main__":
    main()
