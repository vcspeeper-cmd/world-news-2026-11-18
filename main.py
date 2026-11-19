"""Copy entry.png to the output directory specified by MAKEFUN_OUTPUT_DIR or /output."""

import os
import shutil
import sys


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(script_dir, "entry.png")

    if not os.path.isfile(source):
        sys.stderr.write(f"Error: source image not found at {source}\n")
        sys.exit(1)

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip() or "/output"
    os.makedirs(output_dir, exist_ok=True)

    dest = os.path.join(output_dir, "entry.png")
    shutil.copy2(source, dest)


if __name__ == "__main__":
    main()
