# Selenium Test Fixes for ChromeDriver Timeouts

## Problem Description

Selenium tests were intermittently failing on GitHub Actions with `ReadTimeoutError` exceptions. The ChromeDriver process would hang without providing feedback, causing tests to timeout and fail. This particularly affected tests involving websockets and complex page interactions.

## Root Causes

1. **ChromeDriver Hangs**: ChromeDriver can hang in headless mode, especially in resource-constrained CI environments
2. **Insufficient Timeouts**: Default timeout values (3 seconds) were too short for complex operations
3. **WebSocket Delays**: WebSocket communication requires more time to establish connections and propagate updates
4. **Hard-coded Waits**: Use of `time.sleep()` instead of explicit waits led to timing issues

## Solutions Implemented

### 1. WebDriver Timeout Configuration (`tests/utils.py`)

Added explicit timeout configuration to ChromeDriver instances:

```python
def get_chrome_webdriver(cls):
    driver = super().get_chrome_webdriver()
    driver.set_page_load_timeout(60)  # Max time for page loads
    driver.set_script_timeout(60)     # Max time for async scripts
    driver.implicitly_wait(10)        # Element search timeout
    return driver
```

### 2. Configurable Timeout Values (`tests/config.json`)

Added configurable timeout parameters:

- `webdriver_wait_timeout`: 20 seconds (for general WebDriverWait calls)
- `websocket_wait_timeout`: 30 seconds (for websocket-related operations)

### 3. Improved Alert Handling (`tests/utils.py`)

Replaced hard-coded `time.sleep(2)` with explicit wait:

```python
def _ignore_location_alert(self, driver=None):
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        # Handle alert...
    except (NoAlertPresentException, Exception):
        pass  # Timeout or no alert is okay
```

### 4. Dynamic Timeout Usage in Tests

Tests now use configurable timeouts instead of hard-coded values:

```python
timeout = self.config.get("webdriver_wait_timeout", 10)
WebDriverWait(self.base_driver, timeout).until(...)
```

### 5. Restored Tests with Improvements

Re-added the following tests that were removed in PR #581:

- `test_websocket_marker`: Tests real-time location updates via websockets
- `test_topology_graph`: Tests network topology visualization
- `test_create_prefix_users`: Tests RADIUS batch user creation with PDF generation

All restored tests include:
- Increased timeout values
- Explicit waits instead of sleeps
- Better error handling

## Testing Recommendations

### Local Testing

```bash
cd /opt/openwisp/docker-openwisp
make develop-pythontests
```

### CI Testing

The CI workflow already includes retry logic (5 attempts with 30-second delays). With these fixes, tests should pass consistently on the first attempt.

### Timeout Tuning

If tests still timeout in CI:

1. Increase values in `tests/config.json`:
   - `webdriver_wait_timeout`: Increase for general operations
   - `websocket_wait_timeout`: Increase for websocket tests

2. Check ChromeDriver version compatibility
3. Review GitHub Actions runner resource constraints

## Known Issues and Workarounds

### Issue: ChromeDriver Still Hangs

**Workaround**: The CI workflow uses a retry mechanism. If hangs persist:

1. Check ChromeDriver and Selenium versions for compatibility
2. Consider adding `--disable-dev-shm-usage` Chrome option
3. Verify headless mode is properly configured

### Issue: WebSocket Tests Fail Intermittently

**Workaround**: WebSocket connections depend on multiple services:

1. Ensure all containers are healthy before tests
2. Check Redis container status (used for channels)
3. Verify WebSocket container logs for connection issues

## References

- PR #581: Tests removed due to timeout issues
- PR #585: This fix (investigation and resolution)
- Selenium Documentation: https://selenium-python.readthedocs.io/
- ChromeDriver Issues: https://bugs.chromium.org/p/chromedriver/issues/list

## Maintenance Notes

When adding new Selenium tests:

1. Use `self.config.get('webdriver_wait_timeout', 10)` for standard waits
2. Use `self.config.get('websocket_wait_timeout', 30)` for websocket operations
3. Always use explicit waits (`WebDriverWait`) instead of `time.sleep()`
4. Test locally with `SELENIUM_HEADLESS=1` to simulate CI environment
5. Add appropriate timeout parameters to `find_elements()` calls for dynamic content
