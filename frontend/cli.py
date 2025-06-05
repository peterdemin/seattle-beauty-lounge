import argparse
import time

import jinja2.exceptions

from .builder import Builder


def build(builder: Builder, watch: bool, action: str):
    if watch:
        while True:
            try:
                builder.build(action)
            except jinja2.exceptions.TemplateNotFound:
                print("F", end="")
                continue
            print(".", end="")
            time.sleep(0.1)
    else:
        builder.build(action)


def main() -> None:
    parser = argparse.ArgumentParser("frontend", description="Build static website")
    parser.add_argument(
        "mode",
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Run in dev mode, continuously updating (on change)",
    )
    parser.add_argument(
        "-a",
        "--action",
        choices=Builder.get_choices(),
        default="all",
        help="Build target",
    )
    args = parser.parse_args()
    build(Builder(args.mode), args.watch, args.action)


if __name__ == "__main__":
    main()
