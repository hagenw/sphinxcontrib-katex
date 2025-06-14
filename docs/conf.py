# -*- coding: utf-8 -*-
import datetime
import os
import subprocess

import toml

import sphinxcontrib.katex as katex


# -- GENERAL -------------------------------------------------------------
config = toml.load(os.path.join("..", "pyproject.toml"))

project = config["project"]["name"]
author = ", ".join(author["name"] for author in config["project"]["authors"])
year = str(datetime.date.today().year)
copyright = '2017-' + year + ' ' + author

needs_sphinx = '1.6'   # minimal sphinx version
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.katex',
]
master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['_build']

# The full version, including alpha/beta/rc tags.
# release = version
try:
    release = subprocess.check_output(
        ['git', 'describe', '--tags', '--always']
    )
    release = release.decode().strip()
except Exception:
    release = '<unknown>'

# Code syntax highlighting style
pygments_style = 'tango'

linkcheck_ignore = [
    "https://pypi.org/project/sphinxcontrib-katex",
]

# -- ACRONYMS AND MATH ---------------------------------------------------
latex_macros = r"""
    \def \x                {\mathbf{x}}
    \def \w                {\omega}
    \def \d                {\operatorname{d}\!}
"""
katex_macros = katex.latex_defs_to_katex_macros(latex_macros)
katex_options = '{macros: {' + katex_macros + '}, strict: false}'
katex_prerender = False


# -- HTML ----------------------------------------------------------------

html_title = project
html_short_title = ""
htmlhelp_basename = project

# Theme settings,
# see https://insipid-sphinx-theme.readthedocs.io/configuration.html
html_theme = 'insipid'
html_permalinks_icon = '#'
html_copy_source = False
html_show_sourcelink = False
html_use_index = False
html_theme_options = {
    'right_buttons': [
        'fullscreen-button.html',
        'pdf-button.html',
        'repo-button.html',
    ],
}
html_context = {
    'display_github': True,
    'github_user': 'hagenw',
    'github_repo': 'sphinxcontrib-katex',
}

# Extending theme
templates_path = ['_templates']
html_static_path = ['_static']
html_css_files = ['custom.css']


# -- LATEX ---------------------------------------------------------------

# Add arydshln package for dashed lines in array
latex_macros += r'\usepackage{arydshln}'

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'preamble': latex_macros,  # command definitions
    'figure_align': 'htbp',
    'sphinxsetup': (
        'TitleColor={rgb}{0,0,0}, '
        'verbatimwithframe=false, '
        'VerbatimColor={rgb}{.96,.96,.96}'
    ),
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc,
     'sphinxcontrib-katex.tex',
     'sphinxcontrib-katex',
     'sphinxcontrib-katex Development Team',
     'manual',
     True),
]
