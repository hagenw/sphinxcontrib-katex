Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 0.9.8 (2023-10-12)
--------------------------

* Added: support for Python 3.12
* Changed: use KaTeX 0.16.9


Version 0.9.7 (2023-07-03)
--------------------------

* Changed: use KaTeX 0.16.8
* Removed: support for Python 3.7


Version 0.9.6 (2023-06-13)
--------------------------

* Changed: use custom sphinx theme
  based on ``insipid``
  for HTML documentation pages


Version 0.9.5 (2023-06-07)
--------------------------

* Changed: use KaTeX 0.16.7
* Fixed: convert ``KaTeXServer.timeout_error()``
  to class method


Version 0.9.4 (2023-01-04)
--------------------------

* Changed: use KaTeX 0.16.4


Version 0.9.3 (2022-11-25)
--------------------------

* Changed: reverted enforcement of 100% font scale
  as a larger scaling of 1.21em
  is the expected KaTeX default behavior


Version 0.9.2 (2022-11-25)
--------------------------

* Fixed: update Python package version number


Version 0.9.1 (2022-11-25)
--------------------------

* Added: support for Python 3.11
* Changed: use KaTeX 0.16.3
* Changed: enforce 100% of document font-size
  for HTML


Version 0.9.0 (2022-08-19)
--------------------------

* Added: local KaTeX server
  to dramatically speed up pre-rendering
* Added: ``katex.min.js`` and ``auto-render.min.js``
  are now included in the Python package
* Added: support for Python 3.10
* Changed: use KaTeX 0.16.0
* Removed: support for Python 3.6


Version 0.8.6 (2021-05-27)
--------------------------

* Fixed: allow to work with Sphinx>=4.0.0


Version 0.8.5 (2021-05-26)
--------------------------

* Fixed: remove extra space after inline math when using pre-rendering


Version 0.8.4 (2021-05-18)
--------------------------

* Changed: increase top padding of equations by 2px


Version 0.8.3 (2021-05-18)
--------------------------

* Fixed: building of documentation on RTD


Version 0.8.2 (2021-05-18)
--------------------------

* Fixed: PyPI package version number


Version 0.8.1 (2021-05-18)
--------------------------

* Fixed: PyPI package had wrong version number


Version 0.8.0 (2021-05-18)
--------------------------

* Added: support for Python 3.9
* Added: support for Sphinx>=4.0.0
* Added: tests for Windows and macOS
* Changed: switch to KaTeX 0.13.11
* Changed: switched CI tests from Travis to Github Actions
* Changed: running sphinx will now fail in pre-render mode
  if KaTeX fails
* Removed: support for Python 2.7, 3.4, 3.5


Version 0.7.2 (2021-04-28)
--------------------------

* Fixed: Sphinx>=4.0.0 is not supported at the moment


Version 0.7.1 (2020-10-29)
--------------------------

* Fixed: label of fraction example in docs


Version 0.7.0 (2020-10-29)
--------------------------

* Added: fraction example to docs
* Changed: switch to KaTeX 0.12.0
* Changed: add small top and bottom padding to equations


Version 0.6.1 (2020-05-25)
--------------------------

* Fixed: run katex under Windows


Version 0.6.0 (2020-02-13)
--------------------------

* Changed: switch to Katex 0.11.1
* Changed: add tests for Python 3.7 and 3.8


Version 0.5.1 (2019-08-13)
--------------------------

* Added: equation numbers in documentation (#16)
* Changed: subset of tests for sphinx<=1.6 (#23)
* Changed: several improvements to documentation


Version 0.5.0 (2019-07-25)
--------------------------

* Added: katex server side pre-rendering (#15)
* Changed: switch to Katex 0.10.2 (#17)
* Removed: deprecated Sphinx ``setup_math`` (#10)


Version 0.4.1 (2019-01-08)
--------------------------

* Fixed: macros example in documentation


Version 0.4.0 (2018-12-14)
--------------------------

* Added: Sphinx documentation and setup RTD page
* Added: Travis-CI tests
* Changed: KaTeX version 0.10.0
* Changed: make compatible with ``sphinx>=1.6``
* Removed: configuration option ``katex_version``


Version 0.3.1 (2018-10-08)
--------------------------

* Fixed: incompatibility with ``sphinx>=1.8`` (#8)


Version 0.3.0 (2018-09-06)
--------------------------

* Added: allow for user defined autorendering delimiters (#7)
* Fixed: bug if ``katex_options`` was blank (#5)


Version 0.2.0 (2018-06-22)
--------------------------

* Added: document all configuration settings
* Added: automatic setting of delimiters for KaTeX auto-renderer
* Removed: ``katex_macros`` option


Version 0.1.6 (2018-04-12)
--------------------------

* Added: equation numbering across pages with ``sphinx>=1.7``
* Changed: KaTeX version 0.9.0


Version 0.1.5 (2017-12-19)
--------------------------

* Added: helper function to convert LaTeX defs to KaTeX macros
* Changed: improvement of code readability
* Fixed: mouse over for equation numbers in Firefox


Version 0.1.4 (2017-11-27)
--------------------------

* Changed: move equation numbers to the right and center vertically


Version 0.1 (2017-11-24)
------------------------

* Added: initial release


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
