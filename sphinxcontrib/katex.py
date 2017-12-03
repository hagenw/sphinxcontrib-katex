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
import shutil
from docutils import nodes
from tempfile import mkdtemp

from sphinx.locale import _
from sphinx.errors import ExtensionError
from sphinx.util.osutil import copyfile
from sphinx.ext.mathbase import setup_math as mathbase_setup


KATEX_VERSION = '0.9.0-alpha2'
KATEX_JS = 'katex_autorenderer.js'
KATEX_CSS = 'katex-math.css'


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
        self.body.append('<span class="eqno">(%s)' % node['number'])
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
    app.add_javascript(app.config.katex_autorender_path)
    # Write custom autorenderer file
    _write_katex_js_file(app, KATEX_JS)
    app.add_javascript(KATEX_JS)
    # Custom css
    app.add_stylesheet(KATEX_CSS)


def builder_finished(app, exception):
    # Copy custom CSS file
    pwd = os.path.abspath(os.path.dirname(__file__))
    source = os.path.join(pwd, KATEX_CSS)
    dest = os.path.join(app._katex_tmpdir, KATEX_CSS)
    copyfile(source, dest)
    # Delete temporary dir used for _static file
    shutil.rmtree(app._katex_tmpdir)


def _write_katex_js_file(app, js_name):
    static_path = _setup_static_path(app)
    js_file = os.path.join(app.builder.srcdir, static_path, js_name)
    content = _katex_js_content(app)
    with open(js_file, 'w') as file:
        file.write(content)


def _katex_js_content(app):
    content = 'renderMathInElement(document.body, latex_options);'
    macros = app.config.katex_macros
    if len(macros) > 0:
        prefix = 'latex_options = { macros: {'
        suffix = '}}'
        content = '\n'.join([prefix, macros, suffix, content])
    return content


def _setup_static_path(app):
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
    base_path = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/'
    version = KATEX_VERSION
    app.add_config_value('katex_css_path',
                         base_path + version + '/katex.min.css',
                         False)
    app.add_config_value('katex_js_path',
                         base_path + version + '/katex.min.js',
                         False)
    # KaTeX Auto-render extension
    # (github.com/Khan/KaTeX/blob/master/contrib/auto-render/README.md)
    app.add_config_value('katex_autorender_path',
                         base_path + version + '/contrib/auto-render.min.js',
                         False)
    app.add_config_value('katex_inline', [r'\(', r'\)'], 'html')
    app.add_config_value('katex_display', [r'\[', r'\]'], 'html')
    app.add_config_value('katex_macros', '', 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('build-finished', builder_finished)

    return {'version': 0.1, 'parallel_read_safe': True}
