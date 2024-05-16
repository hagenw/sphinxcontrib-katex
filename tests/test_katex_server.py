import os

import pytest

from sphinxcontrib.katex import KaTeXServer


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "katex_js_path, expected_require_path",
    [
        (
            "katex.min.js",
            "./katex.min",
        ),
        (
            "./katex.min.js",
            "./katex.min",
        ),
        (
            os.path.join(".", "katex.min.js"),
            "./katex.min",
        ),
        (
            os.path.join(CURRENT_DIR, "..", "sphinxcontrib", "katex.min.js"),
            "./katex.min",
        ),
    ],
)
def test_katex_server_js_path(katex_js_path, expected_require_path):
    """Test configured KaTeX Javascript library path.

    When using the pre-rendering capabilities
    of the ``sphinxcontrib.katex`` sphinx extension,
    it requires a KaTeX Javascript library
    provided by the file
    specified in the config value ``katex_js_path``.

    Args:
        katex_js_path: path specified for the ``katex_js_path``
            config path variable
        expected_require_path: expected path
            to the KaTeX Javascript library as provided
            to the Javascript ``require()`` function.
            The path needs to be relative
            to the path of ``katex-server.js``
            always starts with ``./``,
            and exclude the file extension

    """
    KaTeXServer.katex_path = katex_js_path
    cmd = KaTeXServer.build_command()
    assert cmd[-1] == expected_require_path


def test_katex_server_js_path_error():
    """Test errors for configured KaTeX Javascript library path."""
    katex_js_path = "non-existing.js"
    error_msg = (
        "KaTeX Javascript library could not be found at "
        f"{os.path.join('.', katex_js_path)}."
    )
    with pytest.raises(ValueError, match=error_msg):
        KaTeXServer.katex_path = katex_js_path
        KaTeXServer.build_command()
