from .javascript_embedder import JavascriptEmbedder


def test_patch_embeds_template() -> None:
    got = JavascriptEmbedder.patch(
        ["a\n", "b\n", "// embed: key\n", "return `\n", "`\n", "}\n"],
        {"key": "value\n"},
    )
    assert got == ["a\n", "b\n", "// embed: key\n", "return `\n", "value\n", "`\n", "}\n"]
