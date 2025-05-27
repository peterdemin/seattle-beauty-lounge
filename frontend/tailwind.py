import subprocess
import tempfile

from .constants import SOURCE_DIR

_CONFIG_TEMPLATE = """
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [CONTENT],
    theme: {
        extend: {
            colors: {
                primary: "rgb(var(--color-primary))",
                secondary: "rgb(var(--color-secondary))",
                neutral: "rgb(var(--color-neutral))",
            },
        },
    },
    plugins: [],
};
"""


class Tailwind:
    STYLES_DIR = f"{SOURCE_DIR}/styles"
    INPUT_CSS = f"./{STYLES_DIR}/input.css"

    def __call__(self, content: list[str], output: str) -> str:
        """Must be called after index.html is rendered"""
        with tempfile.NamedTemporaryFile("wt", encoding="utf-8", delete_on_close=False) as fobj:
            fobj.write(self._render_config(content))
            fobj.close()
            self._run_tailwindcss(fobj.name, output)
        with open(output, "rt", encoding="utf-8") as fobj:
            return fobj.read()

    def _render_config(self, content: list[str]) -> str:
        return _CONFIG_TEMPLATE.replace("CONTENT", ", ".join(f'"{ptrn}"' for ptrn in content))

    def _run_tailwindcss(self, config_path: str, output_path: str) -> None:
        subprocess.run(
            [
                "npx",
                "tailwindcss",
                "-i",
                self.INPUT_CSS,
                "-c",
                config_path,
                "-o",
                output_path,
            ],
            capture_output=True,
            check=True,
        )
