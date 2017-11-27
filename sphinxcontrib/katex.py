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

from sphinx.errors import ExtensionError
from sphinx.ext.mathbase import setup_math as mathbase_setup


katex_version = '0.9.0-alpha2'


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
        self.body.append('<span class="eqno"><a class="equationlink" '
                         'href="#%s" title="Permalink to this '
                         'equation">(%s)</a></span>' %
                         (node['ids'][0], node['number']))
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
    katex_js_name = 'katex_autorenderer.js'
    _write_katex_js_file(app, katex_js_name)
    app.add_javascript(katex_js_name)


def cleanup(app, exception):
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
    version = katex_version
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
    app.connect('build-finished', cleanup)

    return {'version': 0.1, 'parallel_read_safe': True}
