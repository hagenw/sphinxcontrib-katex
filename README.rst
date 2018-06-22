sphinxcontrib-katex
===================

A `Sphinx extension`_ for rendering math in HTML pages.

The extension uses `KaTeX`_ for rendering of math in HTML pages. It is designed
as a replacement for the built-in extension `sphinx.ext.mathjax`_, which uses
`MathJax`_ for rendering.

* Download: https://pypi.python.org/pypi/sphinxcontrib-katex/#downloads

* Development: https://github.com/hagenw/sphinxcontrib-katex/

.. _Sphinx extension: http://www.sphinx-doc.org/en/master/extensions.html
.. _MathJax: https://www.mathjax.org
.. _KaTeX: https://khan.github.io/KaTeX/
.. _sphinx.ext.mathjax:
    https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/mathjax.py


Usage
-----

Installation::

    pip install sphinxcontrib-katex

In ``conf.py`` of your sphinx project, add the extension with:

.. code-block:: python

    extensions = [
        'sphinxcontrib.katex',
        ]


Configuration
-------------

The behavior of the sphinxcontrib.katex can be changed by configuration entries
in the ``conf.py`` file of your documentation project. In the following all
configuration entries are listed and their default values are shown.

.. code-block:: python

    katex_version = 0.9
    katex_css_path = 'https://cdn.jsdelivr.net/npm/katex@' + \
                     katex_version + \
                     '/dist/katex.min.css'
    katex_js_path = 'https://cdn.jsdelivr.net/npm/katex@' + \
                     katex_version + \
                     '/dist/contrib/auto-render.min.js'
    katex_inline = [r'\(', r'\)']
    katex_display = [r'\[', r'\]']
    katex_options = {}

The version of KaTeX used is controlled by the ``katex_version`` config setting,
which per default is also automatically added to the URL strings for the KaTeX
CSS and JS files. The specific delimiters written to HTML when math mode is
encountered are controlled by ``katex_inline`` and ``katex_display``.

The ``katex_options`` setting allows you to change all available official 
`KaTeX rendering options`_.

You can also add `KaTeX auto-rendering options`_ to the ``katex_options``, but
be aware that the ``delimiters`` entry gets always overwritten by the entries of
``katex_inline`` and ``katex_display``.

.. _KaTeX rendering options:
    https://github.com/Khan/KaTeX#rendering-options
.. _KaTeX auto-rendering options: 
    https://github.com/Khan/KaTeX/tree/master/contrib/auto-render#api


LaTeX Macros
------------

Most probably you want to add some ogf your LaTeX math commands for the
rendering. In KaTeX this is supported by LaTeX macros (``\def``).
You can use the ``katex_options`` configuration setting to add those:

.. code-block:: python

    katex_options = {
        r'''macros:  {
            "\\i": "\\mathrm{i}",
            "\\e": "\\mathrm{e}^{#1}",
            "\\vec": "\\mathbf{#1}",
            "\\x": "\\vec{x}",
            "\\d": "\\operatorname{d}\\!{}",
            "\\dirac": "\\operatorname{\\delta}\\left(#1\\right)",
            "\\scalarprod": "\\left\\langle#1,#2\\right\\rangle",
        }
        '''
        }

The disadvantage of this option is that those macros will be only available in
the HTML based `Sphinx builders`_. If you want to use them in the LaTeX based
builders as well you can add them in an extra file in your projet, for example
``definitions.py``:

.. code-block:: python

    latex_macros = r"""
        \def \i                {\mathrm{i}}
        \def \e              #1{\mathrm{e}^{#1}}
        \def \vec            #1{\mathbf{#1}}
        \def \x                {\vec{x}}
        \def \d                {\operatorname{d}\!}
        \def \dirac          #1{\operatorname{\delta}\left(#1\right)}
        \def \scalarprod   #1#2{\left\langle#1,#2\right\rangle}
    """

Note, that we used proper LaTeX syntax here and not the special one required for
``katex_options``. This is fine as ``sphinxcontrib.katex`` provides a function
to translate to the required KaTeX syntax. To use our definitions for HTML and
LaTeX `Sphinx builders`_ add the following to your ``conf.py``.

.. code-block:: python

    import sys

    import sphinxcontrib.katex as katex

    # Allow import/extensions from current path
    sys.path.insert(0, os.path.abspath('.'))
    from definitions import latex_macros

    # Translate LaTeX macros to the required KaTeX format and add to options
    katex_macros = katex.latex_defs_to_katex_macros(latex_macros)
    katex_options = 'macros: {' + katex_macros + '}'

.. _Sphinx builders: http://www.sphinx-doc.org/en/master/builders.html
