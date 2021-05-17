# -*- coding: utf-8 -*-
"""
    sphinxcontrib
    ~~~~~~~~~~~~~

    This package is a namespace package that contains extensions for
    ``sphinx-doc``.

    See https://bitbucket.org/birkenfeld/sphinx-contrib for other extensions.
"""

__all__ = []


# Dynamically get the version of the installed module
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
    __version__ = pkg_resources.get_distribution(__name__).version
except Exception:  # pragma: no cover
    pkg_resources = None  # pragma: no cover
finally:
    del pkg_resources
