import re

from lib.service import Snippet


class JavascriptEmbedder:
    """Updates template strings in .js files from a dictionary."""

    _RE_EMBED = re.compile(r"(?im) *// embed: (\S+)$")
    _RE_END = re.compile(r"(?m) *`$")

    @classmethod
    def __call__(cls, path: str, values: dict[str, Snippet]) -> None:
        with open(path, "r", encoding="utf-8") as fobj:
            lines = list(fobj)
        output = cls.patch(lines, values)
        with open(path, "w", encoding="utf-8") as fobj:
            fobj.writelines(output)

    @classmethod
    def patch(cls, lines: list[str], values: dict[str, Snippet]) -> list[str]:
        output = []
        key = ""
        skip = False
        for line in lines:
            if skip:
                if cls._RE_END.match(line):
                    skip = False
                else:
                    continue
            elif key:
                output.extend([line, values[key].html])
                key, skip = "", True
                continue
            elif mobj := cls._RE_EMBED.match(line):
                key = mobj.group(1)
            output.append(line)
        return output
