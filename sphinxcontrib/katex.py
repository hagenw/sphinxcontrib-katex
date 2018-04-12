# -*- coding: utf-8 -*-
"""
    sphinxcontrib.katex
    ~~~~~~~~~~~~~~~~~~~

    Allow `KaTeX <khan.github.io/KaTeX/>`_ to be used to display math in
    Sphinx's HTML writer.

    :copyright: Copyright 2017 by Hagen Wierstorf.
    :license: MIT, see LICENSE for details.
"""

import os
import re
import shutil
from docutils import nodes
from tempfile import mkdtemp

from sphinx.locale import _
from sphinx.errors import ExtensionError
from sphinx.util.osutil import copyfile
from sphinx.ext.mathbase import setup_math as mathbase_setup
from sphinx.ext.mathbase import get_node_equation_number


__version__ = '0.1.6'
katex_version = '0.9.0'
filename_css = 'katex-math.css'
filename_autorenderer = 'katex_autorenderer.js'


def latex_defs_to_katex_macros(defs):
    r'''Converts LaTeX \def statements to KaTeX macros.

    This is a helper function that can be used in conf.py to translate your
    already specified LaTeX definitions.

    https://github.com/Khan/KaTeX#rendering-options, e.g.
    `\def \e #1{\mathrm{e}^{#1}}` => `"\\e:" "\\mathrm{e}^{#1}"`'

    Example
    -------
    import sphinxcontrib.katex as katex
    # Get your LaTeX defs into `latex_defs` and then do
    katex_macros = katex.import_macros_from_latex(latex_defs)

    '''
    # Remove empty lines
    defs = defs.strip()
    tmp = []
    for line in defs.splitlines():
        # Remove spaces from every line
        line = line.strip()
        # Remove "\def" at the beginning of line
        line = re.sub(r'^\\def[ ]?', '', line)
        # Remove optional #1 parameter before {} command brackets
        line = re.sub(r'(#[0-9])+', '', line, 1)
        # Remove outer {} command brackets with ""
        line = re.sub(r'( {)|(}$)', '"', line)
        # Add "": to the new command
        line = re.sub(r'(^\\[A-Za-z]+)', r'"\1":', line, 1)
        # Add , at end of line
        line = re.sub(r'$', ',', line, 1)
        # Duplicate all \
        line = re.sub(r'\\', r'\\\\', line)
        tmp.append(line)
    macros = '\n'.join(tmp)
    return macros


def html_visit_math(self, node):
    self.body.append(self.starttag(node, 'span', '', CLASS='math'))
    self.body.append(self.builder.config.katex_inline[0] +
                     self.encode(node['latex']) +
                     self.builder.config.katex_inline[1] + '</span>')
    raise nodes.SkipNode


def html_visit_displaymath(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='math'))
    if node['nowrap']:
        self.body.append(self.encode(node['latex']))
        self.body.append('</div>')
        raise nodes.SkipNode

    # necessary to e.g. set the id property correctly
    if node['number']:
        number = get_node_equation_number(self, node)
        self.body.append('<span class="eqno">(%s)' % number)
        self.add_permalink_ref(node, _('Permalink to this equation'))
        self.body.append('</span>')
    self.body.append(self.builder.config.katex_display[0])
    self.body.append(node['latex'])
    self.body.append(self.builder.config.katex_display[1])
    self.body.append('</div>\n')
    raise nodes.SkipNode


def builder_inited(app):
    if not (app.config.katex_js_path and app.config.katex_css_path and
            app.config.katex_autorender_path):
        raise ExtensionError('katex pathes not set')
    app.add_stylesheet(app.config.katex_css_path)
    app.add_javascript(app.config.katex_js_path)
    # Automatic math rendering
    # https://github.com/Khan/KaTeX/blob/master/contrib/auto-render/README.md
    app.add_javascript(app.config.katex_autorender_path)
    write_katex_autorenderer_file(app, filename_autorenderer)
    app.add_javascript(filename_autorenderer)
    # Custom css
    copy_katex_css_file(app, filename_css)
    app.add_stylesheet(filename_css)


def builder_finished(app, exception):
    # Delete temporary dir used for _static file
    shutil.rmtree(app._katex_tmpdir)


def write_katex_autorenderer_file(app, filename):
    static_path = setup_static_path(app)
    filename = os.path.join(app.builder.srcdir, static_path, filename)
    content = katex_autorenderer_content(app)
    with open(filename, 'w') as file:
        file.write(content)


def copy_katex_css_file(app, css_file_name):
    pwd = os.path.abspath(os.path.dirname(__file__))
    source = os.path.join(pwd, css_file_name)
    dest = os.path.join(app._katex_tmpdir, css_file_name)
    copyfile(source, dest)


def katex_autorenderer_content(app):
    content = 'renderMathInElement(document.body, latex_options);'
    macros = app.config.katex_macros
    if len(macros) > 0:
        prefix = 'latex_options = { macros: {'
        suffix = '}}'
        content = '\n'.join([prefix, macros, suffix, content])
    return content


def setup_static_path(app):
    app._katex_tmpdir = mkdtemp()
    static_path = app._katex_tmpdir
    if static_path not in app.config.html_static_path:
        app.config.html_static_path.append(static_path)
    return static_path


def setup(app):
    try:
        mathbase_setup(app, (html_visit_math, None),
                       (html_visit_displaymath, None))
    except ExtensionError:
        raise ExtensionError('katex: other math package is already loaded')

    # Include KaTex CSS and JS files
    katex_url = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/'
    katex_url += katex_version
    app.add_config_value('katex_css_path',
                         katex_url + '/katex.min.css',
                         False)
    app.add_config_value('katex_js_path',
                         katex_url + '/katex.min.js',
                         False)
    app.add_config_value('katex_autorender_path',
                         katex_url + '/contrib/auto-render.min.js',
                         False)
    app.add_config_value('katex_inline', [r'\(', r'\)'], 'html')
    app.add_config_value('katex_display', [r'\[', r'\]'], 'html')
    app.add_config_value('katex_macros', '', 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('build-finished', builder_finished)

    return {'version': __version__, 'parallel_read_safe': True}
