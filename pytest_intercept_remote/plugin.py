import py.path

import pytest

from pytest_intercept_remote import remote_status
from pytest_intercept_remote.fixtures import intercept_skip_conditions, intercept_url
from pytest_intercept_remote.intercept_helpers import intercept_dump, intercept_patch, intercepted_urls


mpatch = pytest.MonkeyPatch()


def pytest_addoption(parser):
    DEFAULT_DUMP_FILE = ".intercepted"

    parser.addoption("--intercept-remote", dest="intercept_remote", action="store_true", default=False,
                     help="Intercepts outgoing connections requests.")
    parser.addoption("--remote-status", dest="remote_status", action="store_true", default=False,
                     help="Reports remote status.")
    parser.addini("intercept_dump_file", "filepath at which intercepted requests are dumped",
                  type="string", default=DEFAULT_DUMP_FILE)


def pytest_configure(config):
    if not config.option.intercept_remote and config.option.verbose:
        print("Intercept outgoing requests: False")

    if config.option.remote_status:
        print("Report remote status: True")

    if config.option.intercept_remote:
        global mpatch
        intercept_patch(mpatch)


def pytest_unconfigure(config):
    """
    Dump requests and clean
    """
    if config.option.intercept_remote:
        global mpatch
        mpatch.undo()
        intercept_dump(config)


def pytest_collection_modifyitems(session, items, config):
    if config.option.remote_status:
        items[:] = []
        report_module = config.hook.pytest_pycollect_makemodule(
            path=py.path.local(remote_status.__file__),
            parent=session)

        items.extend(
            config.hook.pytest_pycollect_makeitem(
                collector=report_module,
                name="test_urls_urllib",
                obj=remote_status.test_urls_urllib))
        items.extend(
            config.hook.pytest_pycollect_makeitem(
                collector=report_module,
                name="test_urls_requests",
                obj=remote_status.test_urls_requests))
        items.extend(
            config.hook.pytest_pycollect_makeitem(
                collector=report_module,
                name="test_urls_socket",
                obj=remote_status.test_urls_socket))
    return
