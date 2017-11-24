sphinxcontrib-katex
===================

A Sphinx extension for rendering math on HTML pages.

The extension uses `KaTeX <https://khan.github.io/KaTeX/>`_ for
rendering of math in HTML pages. Itis designed as a replacement
for mathjax which is slower in rednering, but comes as a build
in extension with sphinx
`sphinx.ext.mathjax
<https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/mathjax.py>`_.

* Download: https://pypi.python.org/pypi/sphinxcontrib-katex/#downloads

* Development: https://github.com/hagenw/sphinxcontrib-katex/


Usage
-----

Installation::

    pip install sphinxcontrib-katex

In your sphinx project, add the extension with:

.. code-block:: python

    extensions = [
        'sphinxcontrib.katex',
        ]

If you would like to add some LaTeX macros (``\def``) you can use the
``katex_macros`` config setting, for example:

.. code-block:: python

    katex_macros = r'''
        "\\i": "\\mathrm{i}",
        "\\e": "\\mathrm{e}^{#1}",
        "\\w": "\\omega",
        "\\vec": "\\mathbf{#1}",
        "\\x": "\\vec{x}",
        "\\d": "\\operatorname{d}\\!{}",
        "\\dirac": "\\operatorname{\\delta}\\left(#1\\right)",
        "\\scalarprod": "\\left\\langle#1,#2\\right\\rangle",
        '''
