# -*- coding: utf-8 -*-
"""
    sphinxcontrib.katex
    ~~~~~~~~~~~~~~~~~~~

    Allow `KaTeX <khan.github.io/KaTeX/>`_ to be used to display math in
    Sphinx's HTML writer.

    :copyright: Copyright 2017 by Hagen Wierstorf.
    :license: MIT, see LICENSE for details.
"""

from docutils import nodes
from os import path

from sphinx.errors import ExtensionError
from sphinx.ext.mathbase import setup_math as mathbase_setup


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
    parts = [prt for prt in node['latex'].split('\n\n') if prt.strip()]
    if len(parts) > 1:  # Add alignment if there are more than 1 equation
        self.body.append(r' \begin{align}\begin{aligned}')
    for i, part in enumerate(parts):
        part = self.encode(part)
        if r'\\' in part:
            self.body.append(r'\begin{split}' + part + r'\end{split}')
        else:
            self.body.append(part)
        if i < len(parts) - 1:  # append new line if not the last equation
            self.body.append(r'\\')
    if len(parts) > 1:  # Add alignment if there are more than 1 equation
        self.body.append(r'\end{aligned}\end{align} ')
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
    app.add_javascript('katex_autorenderer.js')


def setup_autorender(app, exception):
    if app.builder.name != 'html' or exception:
        return
    katex_js_file = path.join(app.builder.outdir,
                              '_static',
                              'katex_autorenderer.js')
    content = 'renderMathInElement(document.body, latex_options);'
    macros = app.config.katex_macros
    if len(macros) > 0:
        content = _add_macros(macros, content)
    with open(katex_js_file, 'w') as file:
        file.write(content)


def _add_macros(macros, content):
    prefix = 'latex_options = { macros: {'
    suffix = '}}'
    return '\n'.join([prefix, macros, suffix, content])


def setup(app):
    try:
        mathbase_setup(app, (html_visit_math, None),
                       (html_visit_displaymath, None))
    except ExtensionError:
        raise ExtensionError('katex: other math package is already loaded')

    # Include KaTex CSS and JS files
    base_path = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/'
    version = '0.9.0-alpha1'
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
    app.connect('build-finished', setup_autorender)

    return {'version': 0.1, 'parallel_read_safe': True}
