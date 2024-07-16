Developer Docs
==============

.. include:: ../partials/developer-docs.rst

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

Building Images
---------------

1. Install Docker and Docker Compose.
2. In the root directory of the repository, run ``make develop``. Once the
   containers are ready, you can test them by accessing the domain names
   of the modules.

.. important::

    - The default username and password are ``admin``.
    - The default domains are ``dashboard.openwisp.org`` and
      ``api.openwisp.org``.
    - To access the dashboard, you may need to add the OpenWISP domains
      specified in your ``.env`` file to your ``hosts`` file. For example,
      run: ``bash -c 'echo "127.0.0.1 dashboard.openwisp.org api.openwisp.org"
      >> /etc/hosts'``
    - You will need to repeat step 2 each time you make changes and want to
      rebuild the images.
    - If you want to perform actions such as cleaning everything produced by
      ``docker-openwisp``, please refer to the :ref:`makefile options
      <docker_image>`.

Running Tests
-------------

You can run tests using either ``geckodriver`` (Firefox) or
``chromedriver`` (Chromium).

**Chromium is preferred as it also checks for console log errors.**

Using Chromedriver
~~~~~~~~~~~~~~~~~~

1. Install Chromium:

   .. code-block:: bash

       # On Debian
       sudo apt --yes install chromium
       # On Ubuntu
       sudo apt --yes install chromium-browser

2. Check the version of Chromium: ``chromium --version``. Then, install
   the corresponding driver from `chromedriver.chromium.org/downloads
   <https://chromedriver.chromium.org/downloads>`_.
3. Extract chromedriver to a directory in your ``$PATH``, e.g.,
   ``/usr/sbin/``.

Using Geckodriver
~~~~~~~~~~~~~~~~~

1. Install Firefox:

   .. code-block:: bash

       sudo apt --yes install firefox

2. Check the version of Firefox: ``firefox --version``. Then, install the
   corresponding driver from `github.com/mozilla/geckodriver/releases
   <https://github.com/mozilla/geckodriver/releases>`_.
3. Extract geckodriver to a directory in your ``$PATH``, e.g.,
   ``/usr/sbin/``.

Finish Setup and Run Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install Selenium:

   .. code-block:: bash

       python3 -m pip install selenium

2. (Optional) Modify configuration options in ``tests/config.json``:

   .. code-block:: yaml

       driver: Name of the driver to use for tests, "chromium" or "firefox"
       logs: Print container logs if an error occurs
       logs_file: Location of the log file for saving logs generated during tests
       headless: Run Selenium Chrome driver in headless mode
       load_init_data: Flag for running tests/data.py, only needs to be done once after database creation
       app_url: URL to reach the admin dashboard
       username: Username for logging into the admin dashboard
       password: Password for logging into the admin dashboard
       services_max_retries: Maximum number of retries to check if services are running
       services_delay_retries: Delay time (in seconds) for each retry when checking if services are running

3. Run tests with:

   .. code-block:: bash

       make runtests

4. To run a single test suite, use the following command:

   .. code-block:: bash

       python3 tests/runtests.py <TestSuite>.<TestCase>

Run Quality Assurance Checks
----------------------------

We use `shfmt <https://github.com/mvdan/sh#shfmt>`__ to format shell
scripts and `hadolint <https://github.com/hadolint/hadolint#install>`__ to
lint Dockerfiles.

To format all files, run:

.. code-block:: bash

    ./qa-format

To run quality assurance checks, use the ``run-qa-checks`` script:

.. code-block:: bash

    # Install test requirements first
    pip install -r requirements-test.txt

    # Run QA checks before committing code
    ./run-qa-checks

.. _docker_image:

Makefile Options
----------------

Most commonly used:

- ``make start [USER=docker-username] [TAG=image-tag]``: Start OpenWISP
  containers on your server.
- ``make pull [USER=docker-username] [TAG=image-tag]``: Pull images from
  the registry.
- ``make stop``: Stop OpenWISP containers on your server.
- ``make develop``: Bundle all the commands required to build the images
  and run containers.
- ``make runtests``: Run test cases to ensure all services are working.
- ``make clean``: Aggressively purge all containers, images, volumes, and
  networks related to ``docker-openwisp``.

Other options:

- ``make publish [USER=docker-username] [TAG=image-tag]``: Build, test,
  and publish images.
- ``make python-build``: Generate a random Django secret and set it in the
  ``.env`` file.
- ``make nfs-build``: Build the OpenWISP NFS server image.
- ``make base-build``: Build the OpenWISP base image. The base image is
  used in other OpenWISP images.
- ``make compose-build``: (default) Build OpenWISP images for development.
- ``make develop-runtests``: Similar to ``runtests``, but it doesn't stop
  the containers after running the tests, which may be desired for
  debugging and analyzing failing container logs.
