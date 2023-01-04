# -*- coding: utf-8 -*-
"""
    sphinxcontrib.katex
    ~~~~~~~~~~~~~~~~~~~

    Allow `KaTeX <khan.github.io/KaTeX/>`_ to be used to display math in
    Sphinx's HTML writer.

    :copyright: Copyright 2017-2022 by Hagen Wierstorf.
    :license: MIT, see LICENSE for details.
"""

import atexit
import json
import os
import re
import shutil
from docutils import nodes
from tempfile import mkdtemp
from textwrap import dedent
import socket
import struct
import tempfile
import time

from contextlib import closing, contextmanager
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

from sphinx.locale import _
from sphinx.errors import ExtensionError
from sphinx.util.osutil import copyfile


__version__ = '0.9.4'
katex_version = '0.16.4'
filename_css = 'katex-math.css'
filename_autorenderer = 'katex_autorenderer.js'
SRC_DIR = Path(__file__).parent
SCRIPT_PATH = str(SRC_DIR / "katex-server.js")

ONE_MILLISECOND = 0.001

TIMEOUT_EXPIRED_TEMPLATE = (
    "Rendering {} is taking too long. Try increasing RENDER_TIMEOUT"
)

STARTUP_TIMEOUT_EXPIRED = (
    "KaTeX server did not came up after {} seconds. "
    "Try increasing STARTUP_TIMEOUT."
)

KATEX_DEFAULT_OPTIONS = {
    # Prefer KaTeX's debug coloring by default. This will not raise exceptions.
    "throwOnError": False
}

KATEX_PATH = None

# How long to wait for the render server to start in seconds
STARTUP_TIMEOUT = 5.0

# Timeout per rendering request in seconds
RENDER_TIMEOUT = 5.0

# nodejs binary to run javascript
NODEJS_BINARY = "node"


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
    latex_macros = katex.import_macros_from_latex(latex_defs)
    katex_options = 'macros: {' + latex_macros + '}'
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


def get_latex(node):
    if 'latex' in node.attributes:
        return node['latex']  # for Sphinx < 1.8.0
    else:
        return node.astext()  # for Sphinx >= 1.8.0


def html_visit_math(self, node):
    self.body.append(self.starttag(node, 'span', '', CLASS='math'))

    if self.builder.config.katex_prerender:
        self.body.append(render_latex(get_latex(node)))
    else:
        self.body.append(
            self.builder.config.katex_inline[0]
            + self.encode(get_latex(node))
            + self.builder.config.katex_inline[1]
        )

    self.body.append('</span>')
    raise nodes.SkipNode


def html_visit_displaymath(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='math'))

    # necessary to e.g. set the id property correctly
    if node['number']:
        number = get_node_equation_number(self, node)
        self.body.append('<span class="eqno">(%s)' % number)
        self.add_permalink_ref(node, _('Permalink to this equation'))
        self.body.append('</span>')

    if self.builder.config.katex_prerender:
        # NB: nowrap is always "on" when using prerendering
        self.body.append(render_latex(get_latex(node), {"displayMode": True}))
        self.body.append('</div>')
    elif node['nowrap']:
        self.body.append(self.encode(get_latex(node)))
        self.body.append('</div>')
    else:
        self.body.append(self.builder.config.katex_display[0])
        self.body.append(get_latex(node))
        self.body.append(self.builder.config.katex_display[1])
        self.body.append('</div>\n')

    raise nodes.SkipNode


def builder_inited(app):
    if not (
            app.config.katex_js_path
            and app.config.katex_css_path
            and app.config.katex_autorender_path
    ):
        raise ExtensionError('KaTeX paths not set')
    # Sphinx 1.8 renamed `add_stylesheet` to `add_css_file`
    # and `add_javascript` to `add_js_file`.
    # Sphinx 4.0 finally removed `add_stylesheet` and `add_javascript`.
    old_css_add = getattr(app, 'add_stylesheet', None)
    old_js_add = getattr(app, 'add_javascript', None)
    add_css = getattr(app, 'add_css_file', old_css_add)
    add_js = getattr(app, 'add_js_file', old_js_add)
    # Ensure the static path is setup to hold KaTeX CSS and autorender files
    setup_static_path(app)
    # KaTeX CSS
    add_css(app.config.katex_css_path)
    if not app.config.katex_prerender:
        # KaTeX JS
        add_js(app.config.katex_js_path)
        copy_file(app, app.config.katex_js_path)
        # KaTeX auto-renderer
        add_js(app.config.katex_autorender_path)
        copy_file(app, app.config.katex_autorender_path)
        # Automatic math rendering and custom CSS
        # https://github.com/Khan/KaTeX/blob/master/contrib/auto-render/README.md
        write_katex_autorenderer_file(app, filename_autorenderer)
        add_js(filename_autorenderer)
    # sphinxcontrib.katex custom CSS
    copy_file(app, filename_css)
    add_css(filename_css)


def builder_finished(app, exception):
    # Delete temporary dir used for _static file
    shutil.rmtree(app._katex_static_path)


def write_katex_autorenderer_file(app, filename):
    filename = os.path.join(
        app.builder.srcdir, app._katex_static_path, filename
    )
    content = katex_autorenderer_content(app)
    with open(filename, 'w') as file:
        file.write(content)


def copy_file(app, file_name):
    r"""Copy file to statis path."""
    pwd = os.path.abspath(os.path.dirname(__file__))
    source = os.path.join(pwd, file_name)
    dest = os.path.join(app._katex_static_path, file_name)
    copyfile(source, dest)


def katex_autorenderer_content(app):
    content = dedent('''\
        document.addEventListener("DOMContentLoaded", function() {
          renderMathInElement(document.body, katex_options);
        });
        ''')
    prefix = 'katex_options = {'
    suffix = '}'
    options = katex_rendering_options(app)
    delimiters = katex_rendering_delimiters(app)
    return '\n'.join([prefix, options, delimiters, suffix, content])


def katex_rendering_delimiters(app):
    """Delimiters for rendering KaTeX math.

    If no delimiters are specified in katex_options, add the
    katex_inline and katex_display delimiters. See also
    https://khan.github.io/KaTeX/docs/autorender.html
    """
    # Return if we have user defined rendering delimiters
    if 'delimiters' in app.config.katex_options:
        return ''
    katex_inline = [d.replace('\\', '\\\\') for d in app.config.katex_inline]
    katex_display = [d.replace('\\', '\\\\') for d in app.config.katex_display]
    katex_delimiters = {'inline': katex_inline, 'display': katex_display}
    # Set chosen delimiters for the auto-rendering options of KaTeX
    delimiters = r'''delimiters: [
        {{ left: "{inline[0]}", right: "{inline[1]}", display: false }},
        {{ left: "{display[0]}", right: "{display[1]}", display: true }}
        ]'''.format(**katex_delimiters)
    return delimiters


def katex_rendering_options(app):
    """Strip katex_options from enclosing {} and append ,"""
    options = trim(app.config.katex_options)
    # Remove surrounding {}
    if options.startswith('{') and options.endswith('}'):
        options = trim(options[1:-1])
    # If options is not empty, ensure it ends with ','
    if options and not options.endswith(','):
        options += ','
    return options


def trim(text):
    """Remove whitespace from both sides of a string."""
    return text.lstrip().rstrip()


def setup_static_path(app):
    app._katex_static_path = mkdtemp()
    if app._katex_static_path not in app.config.html_static_path:
        app.config.html_static_path.append(app._katex_static_path)


def setup(app):
    try:
        app.add_html_math_renderer(
            'katex',
            inline_renderers=(html_visit_math, None),
            block_renderers=(html_visit_displaymath, None)
        )
    except AttributeError:
        # Versions of sphinx<1.8 require setup_math instead
        from sphinx.ext.mathbase import setup_math
        setup_math(app, (html_visit_math, None),
                   (html_visit_displaymath, None))

    # Include KaTex CSS and JS files
    katex_url = 'https://cdn.jsdelivr.net/npm/katex@{version}/dist/'.format(
        version=katex_version
    )
    app.add_config_value(
        'katex_css_path',
        katex_url + 'katex.min.css',
        False,
    )
    app.add_config_value('katex_js_path', 'katex.min.js', False)
    app.add_config_value('katex_autorender_path', 'auto-render.min.js', False)
    app.add_config_value('katex_inline', [r'\(', r'\)'], 'html')
    app.add_config_value('katex_display', [r'\[', r'\]'], 'html')
    app.add_config_value('katex_options', '', 'html')
    app.add_config_value('katex_prerender', False, 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('build-finished', builder_finished)

    return {'version': __version__, 'parallel_read_safe': True}


# This function is copied from Sphinx 1.8 as it is not available in Sphinx 1.6
def get_node_equation_number(writer, node):
    if writer.builder.config.math_numfig and writer.builder.config.numfig:
        figtype = 'displaymath'
        if writer.builder.name == 'singlehtml':
            key = u"%s/%s" % (writer.docnames[-1], figtype)
        else:
            key = figtype

        id = node['ids'][0]
        number = writer.builder.fignumbers.get(key, {}).get(id, ())
        number = '.'.join(map(str, number))
    else:
        number = node['number']

    return number


@contextmanager
def socket_timeout(sock, timeout):
    """Set the timeout on a socket for a context and restore it afterwards"""

    original = sock.gettimeout()
    try:
        sock.settimeout(timeout)

        yield
    finally:
        sock.settimeout(original)


def random_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        # reuse sockets
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # choose port=0 for random port
        sock.bind(("127.0.0.1", 0))

        # return port
        _, p = sock.getsockname()
        return p


class KaTeXError(Exception):
    pass


class KaTeXServer:
    """Manages and communicates with an instance of the render server"""

    # Message length is 32-bit little-endian integer
    LENGTH_STRUCT = struct.Struct("<i")

    # global instance
    KATEX_SERVER = None

    # wait for the server to stop in seconds
    STOP_TIMEOUT = 0.1

    @staticmethod
    def timeout_error(self, timeout):
        message = STARTUP_TIMEOUT_EXPIRED.format(timeout)
        return KaTeXError(message)

    @staticmethod
    def build_command(socket=None, port=None):
        cmd = [NODEJS_BINARY, SCRIPT_PATH]

        if socket is not None:
            cmd.extend(["--socket", str(socket)])

        if port is not None:
            cmd.extend(["--port", str(port)])

        if KATEX_PATH:
            cmd.extend(["--katex", str(KATEX_PATH)])

        return cmd

    @classmethod
    def start_server_process(cls, rundir, timeout):
        socket_path = rundir / "katex.sock"

        # Start the server process
        cmd = cls.build_command(socket=socket_path)
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, cwd=rundir)

        # Wait for the server to come up and create the socket.
        startup_start = time.monotonic()
        while not socket_path.is_socket():
            time.sleep(ONE_MILLISECOND)
            if time.monotonic() - startup_start > timeout:
                raise cls.timeout_error(timeout)

        # Connect to the server through a unix socket
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            remaining = startup_start + timeout - time.monotonic()
            with socket_timeout(sock, remaining):
                sock.connect(str(socket_path))
        except socket.timeout:
            raise cls.timeout_error(timeout)

        return process, sock

    @classmethod
    def start_network_socket(cls, rundir, timeout):
        # Start the server on a random free port and connect to it.
        # The port may become unavailable in between the check and usage.
        host = "127.0.0.1"
        port = random_free_port()

        # Start the server process
        cmd = cls.build_command(port=port)
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, cwd=rundir)

        # Connect to the server through a network socket. We need to wait for
        # the server to create the server socket. A nicer solution which would
        # also side-step the race condition would be for the server to select
        # the random port and then print it to stdout. Then python could
        # select() on stdout to wait for the port/socket path without resorting
        # to polling. However, select() is not supported for pipes on Windows.
        startup_start = time.monotonic()
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remaining = startup_start + timeout - time.monotonic()
                if remaining <= 0.0:
                    raise cls.timeout_error(timeout)

                with socket_timeout(sock, remaining):
                    sock.connect((host, port))

                break
            except ConnectionRefusedError:
                # The server is not up yet. Try again.
                time.sleep(ONE_MILLISECOND)
            except socket.timeout:
                raise cls.timeout_error(timeout)

        return process, sock

    @classmethod
    def start(cls):
        rundir = Path(tempfile.mkdtemp(prefix="sphinxcontrib_katex"))

        if os.name == "posix":
            process, sock = cls.start_server_process(rundir, STARTUP_TIMEOUT)
        else:
            # Non-unix systems (i.e. Windows) do not support unix
            # domain sockets for IPC, so we use network sockets.
            process, sock = cls.start_network_socket(rundir, STARTUP_TIMEOUT)

        server = KaTeXServer(rundir, process, sock)

        # Clean up after ourselves when skphinx is done.
        # I don't want to register signal handlers here.
        atexit.register(KaTeXServer.terminate, server)

        return server

    @classmethod
    def get(cls):
        """Get the current render server or start one"""
        if cls.KATEX_SERVER is None:
            cls.KATEX_SERVER = KaTeXServer.start()

        return cls.KATEX_SERVER

    def __init__(self, rundir, process, sock):
        self.rundir = rundir
        self.process = process
        self.sock = sock

        # 100KB should be large enough even for big equations
        self.buffer = bytearray(100 * 1024)

    def terminate(self):
        """Terminate the render server and clean up"""
        self.sock.close()
        try:
            self.process.terminate()
            self.process.wait(timeout=self.STOP_TIMEOUT)
        except TimeoutExpired:
            self.process.kill()
        shutil.rmtree(self.rundir)

    def render(self, request, timeout=None):
        # Configure timeouts
        if timeout is not None:
            start_time = time.monotonic()
            self.sock.settimeout(timeout)
        else:
            self.sock.settimeout(None)

        # Send the request
        request_bytes = json.dumps(request).encode("utf-8")
        length = len(request_bytes)
        self.sock.sendall(self.LENGTH_STRUCT.pack(length))
        self.sock.sendall(request_bytes)

        # Read the amount of bytes we are about to receive
        size = self.sock.recv(self.LENGTH_STRUCT.size)
        length = self.LENGTH_STRUCT.unpack(size)[0]

        # Ensure that the buffer is large enough
        if len(self.buffer) < length:
            self.buffer = bytearray(length)

        with memoryview(self.buffer) as view:
            # Keep reading from the socket until we have received all bytes
            received = 0
            remaining = length
            while remaining > 0:
                # Abort if we are not done yet but the timeout has expired
                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    if elapsed >= timeout:
                        raise socket.timeout()
                    else:
                        # Subsequent recvs only get the remaining time instead
                        # of the whole timeout again
                        self.sock.settimeout(timeout - elapsed)

                n_received = self.sock.recv_into(
                    view[received:length],
                    remaining,
                )
                received += n_received
                remaining -= n_received

            # Decode the response
            serialized = view[:length].tobytes().decode("utf-8")
            return json.loads(serialized)


def render_latex(latex, options=None):
    """Ask the KaTeX server to render some LaTeX.

    Parameters
    ----------
    latex : str
        LaTeX to render
    options : optional dict
        KaTeX options such as displayMode
    """

    # Combine caller-defined options with the default options
    katex_options = KATEX_DEFAULT_OPTIONS
    if options is not None:
        katex_options = katex_options.copy()
        katex_options.update(options)

    server = KaTeXServer.get()
    request = {"latex": latex, "katex_options": katex_options}

    try:
        response = server.render(request, RENDER_TIMEOUT)

        if "html" in response:
            return response["html"]
        elif "error" in response:
            raise KaTeXError(response["error"])
        else:
            raise KaTeXError("Unknown response from KaTeX renderer")
    except socket.timeout:
        raise KaTeXError(TIMEOUT_EXPIRED_TEMPLATE.format(latex))
