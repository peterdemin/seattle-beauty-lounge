from lib.service import Snippet

from .javascript_embedder import JavascriptEmbedder


def test_patch_embeds_template() -> None:
    got = JavascriptEmbedder.patch(
        ["a\n", "b\n", "// embed: key\n", "return `\n", "`;\n", "}\n"],
        {"key": Snippet(html="value\n", full_index="", plain_text="")},
    )
    assert got == ["a\n", "b\n", "// embed: key\n", "return `\n", "value\n", "`;\n", "}\n"]
