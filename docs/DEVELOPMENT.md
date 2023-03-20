# Development

## Workbench setup

1. Install docker & docker-compose.
2. In the root of the repository, run `make develop`, when the containers are ready, you can test them out by going to the domain name of the modules.

**Notes:**

- Default username & password are `admin`.
- Default domains are: `dashboard.openwisp.org` and `api.openwisp.org`.
- To reach the dashboard you may need to add the openwisp domains set in your `.env` to your `hosts` file,
  example: `bash -c 'echo "127.0.0.1 dashboard.openwisp.org api.openwisp.org" >> /etc/hosts'`
- Now you'll need to do steps (2) everytime you make a changes and want to build the images again.
- If you want to perform actions like cleaning everything produced by `docker-openwisp`,
  please use the [makefile options](#makefile-options).

## Runtests

You can run tests either with `geckodriver` (firefox) or `chromedriver` (chromium). Chromium is preferred as it checks for console log errors as well.

1. Setup driver for selenium:

   - Setup chromedriver

     1. Install chromium:

     ```bash
     # On debian
     sudo apt --yes install chromium
     # On ubuntu
     sudo apt --yes install chromium-browser
     ```

     3. Check version: `chromium --version`
     4. Install Driver for your version: [`https://chromedriver.chromium.org/downloads`](https://chromedriver.chromium.org/downloads)
     5. Extract chromedriver to one of directories from your `$PATH`. (example: `/usr/bin/`)

   - Setup geckodriver

     1. Install: `sudo apt --yes install firefox`
     2. Check version: `firefox --version`
     3. Install Driver for your version: [`https://github.com/mozilla/geckodriver/releases`](https://github.com/mozilla/geckodriver/releases)
     4. Extract geckodriver to one of directories from your `$PATH`. (example: `/usr/bin/`)

2. Install selenium: `python3 -m pip install selenium`

3. (Optional) Configure: open `tests/config.json` and configure variables as per your requirement, options are:

   ```yaml
   driver: Name of driver to use for tests, "chromium" or "firefox"
   logs: print container's logs if an error occurs.
   logs_file: Location of the log file for saving logs generated for tests.
   headless: Run selenium chrome driver in headless mode
   load_init_data: Flag for running tests/data.py, only needs to be done once after database creation
   app_url: URL to reach the admin dashboard
   username: username for logging in admin dashboard
   password: password for logging in admin dashboard
   services_max_retries: Maximum number of retries to check if services are running
   services_delay_retries: Delay time (in seconds) to each retries for checking if services are running
   ```

4. Run tests: `make runtests`

**Note:** To run a single test use the following command

```bash
python3 tests/runtests.py <TestSuite>.<TestCase>
# python3 tests/runtests.py TestServices.test_celery
```

## Run Quality Assurance Checks

We use [shfmt](https://github.com/mvdan/sh#shfmt) to format shell scripts and
[hadolint](https://github.com/hadolint/hadolint#install) to lint Dockerfile

To format all files, Run:

```
./qa-format
```

To run quality assurance checks you can use the `run-qa-checks` script:

```
# install test requirements first
pip install requirements-test.txt

# run QA checks before committing code
./run-qa-checks
```
