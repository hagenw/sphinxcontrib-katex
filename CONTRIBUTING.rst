Contributing
------------

If you find errors, omissions, inconsistencies or other things that need
improvement, please create an issue or a pull request at
https://github.com/hagenw/sphinxcontrib-katex/.
Contributions are always welcome!


Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^

Instead of pip-installing the latest release from PyPI, you should get the
newest development version from Github_::

   git clone https://github.com/hagenw/sphinxcontrib-katex.git
   cd sphinxcontrib-katex
   # Create virtual environment
   pip install -r requirements.txt

.. _Github: https://github.com/hagenw/sphinxcontrib-katex/

This way, your installation always stays up-to-date, even if you pull new
changes from the Github repository.


Coding Convention
^^^^^^^^^^^^^^^^^

We follow the PEP8_ convention for Python code
and check for correct syntax with ruff_.
In addition,
we check for common spelling errors with codespell_.
Both tools and possible exceptions
are defined in :file:`pyproject.toml`.

The checks are executed in the CI using `pre-commit`_.
You can enable those checks locally by executing::

    pip install pre-commit  # consider system wide installation
    pre-commit install
    pre-commit run --all-files

Afterwards ruff_ and codespell_ are executed
every time you create a commit.

You can also install ruff_ and codespell_
and call it directly::

    pip install ruff codespell  # consider system wide installation
    ruff check .
    codespell

It can be restricted to specific files::

    ruff check sphinxcontrib/katex.py
    codespell sphinxcontrib/katex.py


.. _codespell: https://github.com/codespell-project/codespell/
.. _PEP8: http://www.python.org/dev/peps/pep-0008/
.. _pre-commit: https://pre-commit.com
.. _ruff: https://beta.ruff.rs


Building the Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you make changes to the documentation, you can re-create the HTML pages
using Sphinx_.
You can install it and a few other necessary packages with::

   pip install -r docs/requirements.txt

To create the HTML pages, use::

   python -m sphinx docs/ build/sphinx/ -b html

The generated files will be available in the directory ``build/sphinx/``.

It is also possible to automatically check if all links are still valid::

   python -m sphinx docs/ build/sphinx/ -b linkcheck

.. _Sphinx: http://sphinx-doc.org/


Running Tests
^^^^^^^^^^^^^

``sphinxcontrib.katex`` is supposed to work for all versions ``sphinx>=1.6``.
To test that you have to use a stripped down version of the documentation that
is provided in the ``tests/`` folder, as the documentation under ``docs/`` uses
features that are only supported by ``sphinx>=1.8``.

To test that everything works as expected, please execute:

.. code-block:: bash

   python -m sphinx tests/ tests/_build/ -c docs/ -b html -W
   python -m sphinx tests/ tests/_build/ -c docs/ -b latex -W

The same tests are automatically performed once you create a pull
request on Github_.


Updating to a new KaTeX version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``sphinxcontrib.katex`` is bond to fixed KaTeX versions.
To update the package to a new KaTeX version,
execute:

.. code-block:: bash

    bash update-katex-version.sh

and commit the resulting changes.


Creating a New Release
^^^^^^^^^^^^^^^^^^^^^^

New releases are made using the following steps:

#. Bump version number in ``sphinxcontrib/katex.py``
#. Update ``CHANGELOG.rst``
#. Commit those changes as "Release X.Y.Z"
#. Create an (annotated) tag with ``git tag -a vX.Y.Z``
#. Push the commit and the tag to Github
#. Check that the new release was built correctly on RTD_, delete the "stable"
   version and select the new release as default version

.. _RTD: http://readthedocs.org/projects/sphinxcontrib-katex/builds/
