import subprocess

from .constants import SOURCE_DIR


class Tailwind:
    STYLES_DIR = f"{SOURCE_DIR}/styles"
    INPUT_CSS = f"./{STYLES_DIR}/input.css"

    def __call__(self, config: str, output: str) -> str:
        """Must be called after index.html is rendered"""
        subprocess.run(
            [
                "npx",
                "tailwindcss",
                "-i",
                self.INPUT_CSS,
                "-c",
                config,
                "-o",
                output,
            ],
            capture_output=True,
            check=True,
        )
        with open(output, "rt", encoding="utf-8") as fobj:
            return fobj.read()
