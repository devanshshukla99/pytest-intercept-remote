import json
import os.path
import tempfile
import pytest
import inspect

mpatch = pytest.MonkeyPatch()

_requests_urls = []
_sockets_urls = []
_urllib_urls = []


def pytest_addoption(parser):
    # DEFAULT_DUMP_FILE = "remote_urls.json"

    parser.addoption("--intercept-remote", dest="intercept_remote", action="store_true", default=False,
                     help="Intercepts outgoing connections requests.")
    parser.addoption("--remote-status", dest="remote_status", action="store", nargs='?',
                     const="show", default="show", type=str, help="Show remote status (show/only/no).")
    parser.addini("intercept_dump_file", "filepath at which intercepted requests are dumped",
                  type="string", default=None)


def pytest_collection_modifyitems(items, config):
    if config.option.remote_status == 'only':
        config.hook.pytest_deselected(items=items)
        items[:] = []
        intercept_dump(config)


def pytest_configure(config):
    if not config.option.intercept_remote and config.option.verbose:
        print("Intercept outgoing requests: disabled")

    intercept_remote = config.getoption('--intercept-remote')

    if intercept_remote:
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


def urlopen_mock(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    global _urllib_urls
    _urllib_urls.append(req.get_full_url())
    pytest.xfail(f"The test was about to call {req.get_full_url()}")


def requests_mock(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
    global _requests_urls
    full_url = f"{self.scheme}://{self.host}{url}"
    _requests_urls.append(full_url)
    pytest.xfail(f"The test was about to {method} {full_url}")


def socket_connect_mock(self, addr):
    """
    Mock function for socket.socket.
    """
    global _sockets_urls
    self.close()
    host = addr[0]
    port = addr[1]
    _sockets_urls.append(addr)
    pytest.xfail(f"The test was about to connect to {host}:{port}")


def intercept_patch(mpatch):
    """
    Monkey Patches urllib, urllib3 and socket.
    """
    mpatch.setattr(
        "urllib.request.AbstractHTTPHandler.do_open", urlopen_mock)
    mpatch.setattr(
        "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock)
    mpatch.setattr(
        "socket.socket.connect", socket_connect_mock)


@pytest.fixture
def intercepted_urls():
    """
    Pytest fixture to get the list of intercepted urls in a test
    """
    _urls = {
        'urls_urllib': _urllib_urls,
        'urls_requests': _requests_urls,
        'urls_socket': _sockets_urls}
    return _urls


def intercept_dump(config):
    """
    Dumps intercepted requests to ini option ``intercept_dump_file``.
    """
    global _requests_urls, _urllib_urls, _sockets_urls

    _urls = {
        'urls_urllib': _urllib_urls,
        'urls_requests': _requests_urls,
        'urls_socket': _sockets_urls}

    if config.getini("intercept_dump_file") and config.option.intercept_remote:
        with open(config.getini("intercept_dump_file"), 'w') as fd:
            json.dump(_urls, fd)

    if config.option.remote_status != 'no':
        if config.getini("intercept_dump_file"):
            fd = open(config.getini("intercept_dump_file"))
            _urls = json.load(fd)
            fd.close()

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_remote_urls.py"), 'w') as fd:
                fd.write(inspect.cleandoc(f"""
                    import socket
                    from urllib.error import HTTPError, URLError
                    from urllib.request import urlopen

                    import pytest
                    import requests

                    intercepted_urls = {_urls}

                    @pytest.mark.parametrize("url", intercepted_urls.get('urls_urllib', ''))
                    def test_urls_urllib(url):
                        try:
                            res = urlopen(url)
                            assert res.status == 200
                        except (HTTPError,URLError) as e:
                            pytest.xfail(f"URL unreachable, status:{{e.reason}}")

                    @pytest.mark.parametrize("url", intercepted_urls.get('urls_requests', ''))
                    def test_urls_requests(url):
                        try:
                            res = requests.get(url)
                            status = res.status_code
                            if status != 200:
                                pytest.xfail(f"URL unreachable, status:{{status}}")
                                return
                            assert res.status_code == 200
                        except requests.exceptions.ConnectionError as e:
                            pytest.xfail(f"URL unreachable")

                    @pytest.mark.parametrize("url", intercepted_urls.get('urls_socket', ''))
                    def test_urls_socket(url):
                        sock = socket.socket(socket.AF_INET)
                        if len(url) == 4:
                            sock = socket.socket(socket.AF_INET6)
                        try:
                            assert sock.connect(tuple(url)) is None
                        except ConnectionRefusedError:
                            pytest.xfail("URL unreachable")
                        finally:
                            sock.close()

                    """))

            pytest.main([tmpdir, "-v", "--tb=no", "-s"])
