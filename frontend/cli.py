import sys
import time

import jinja2.exceptions

from .builder import Builder


def build(mode: str = "development", watch: bool = False):
    builder = Builder(mode)
    if watch:
        while True:
            try:
                builder.build_public()
            except jinja2.exceptions.TemplateNotFound:
                print("F", end="")
                continue
            print(".", end="")
            time.sleep(0.1)
    else:
        builder.build_public()


def main() -> None:
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        raise RuntimeError("Pass mode [development|staging|production] as the first parameter")
    watch = False
    if len(sys.argv) > 2 and sys.argv[2] == "watch":
        watch = True
    build(mode, watch)


if __name__ == "__main__":
    main()
