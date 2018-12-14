sphinxcontrib-katex
===================

A `Sphinx extension`_ for rendering math in HTML pages.

The extension uses `KaTeX`_ for rendering of math in HTML pages. It is designed
as a replacement for the built-in extension `sphinx.ext.mathjax`_, which uses
`MathJax`_ for rendering.

* Documentation: https://sphinxcontrib-katex.readthedocs.io/

* Download: https://pypi.org/project/sphinxcontrib-katex/#files

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

    extensions = ['sphinxcontrib.katex']


Configuration
-------------

The behavior of ``sphinxcontrib.katex`` can be changed by configuration
entries in ``conf.py`` of your documentation project. In the following
all configuration entries are listed and their default values are shown.

.. code-block:: python

    katex_css_path = \
        'https://cdn.jsdelivr.net/npm/katex@0.10/dist/katex.min.css'
    katex_js_path = \
        'https://cdn.jsdelivr.net/npm/katex@0.10/dist/katex.min.js'
    katex_autorender_path = \
        'https://cdn.jsdelivr.net/npm/katex@0.10/contrib/auto-render.min.js'
    katex_inline = [r'\(', r'\)']
    katex_display = [r'\[', r'\]']
    katex_options = ''

The specific delimiters written to HTML when math mode is encountered are
controlled by the two lists ``katex_inline`` and ``katex_display``.

The string variable ``katex_options`` allows you to change all available
official `KaTeX rendering options`_, e.g.

.. code-block:: python

    katex_options = r'''{
        displayMode: true,
        macros: {
            "\\RR": "\\mathbb{R}"
        }
    }'''

You can also add `KaTeX auto-rendering options`_ to ``katex_options``, but be
aware that the ``delimiters`` entry should contain the entries of
``katex_inline`` and ``katex_display``.

.. _KaTeX rendering options:
    https://khan.github.io/KaTeX/docs/options.html
.. _KaTeX auto-rendering options:
    https://khan.github.io/KaTeX/docs/autorender.html


LaTeX Macros
------------

Most probably you want to add some of your LaTeX math commands for the
rendering. In KaTeX this is supported by LaTeX macros (``\def``).
You can use the ``katex_options`` configuration setting to add those:

.. code-block:: python

    katex_options = r'''macros: {
            "\\i": "\\mathrm{i}",
            "\\e": "\\mathrm{e}^{#1}",
            "\\vec": "\\mathbf{#1}",
            "\\x": "\\vec{x}",
            "\\d": "\\operatorname{d}\\!{}",
            "\\dirac": "\\operatorname{\\delta}\\left(#1\\right)",
            "\\scalarprod": "\\left\\langle#1,#2\\right\\rangle",
        }'''

The disadvantage of this option is that those macros will be only available in
the HTML based `Sphinx builders`_. If you want to use them in the LaTeX based
builders as well you have to add them as the ``latex_macros`` setting in your
``conf.py`` and specify them using proper LaTeX syntax. Afterwards you can
include them via the ``sphinxcontrib.katex.latex_defs_to_katex_macros``
function into ``katex_options`` and add them to the LaTeX preamble:

.. code-block:: python

    import sphinxcontrib.katex as katex

    latex_macros = r"""
        \def \i                {\mathrm{i}}
        \def \e              #1{\mathrm{e}^{#1}}
        \def \vec            #1{\mathbf{#1}}
        \def \x                {\vec{x}}
        \def \d                {\operatorname{d}\!}
        \def \dirac          #1{\operatorname{\delta}\left(#1\right)}
        \def \scalarprod   #1#2{\left\langle#1,#2\right\rangle}
    """

    # Translate LaTeX macros to KaTeX and add to options for HTML builder
    katex_macros = katex.latex_defs_to_katex_macros(latex_macros)
    katex_options = 'macros: {' + katex_macros + '}'

    # Add LaTeX macros for LATEX builder
    latex_elements = {'preamble': latex_macros}

.. _Sphinx builders: http://www.sphinx-doc.org/en/master/builders.html
