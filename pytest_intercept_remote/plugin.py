import json
import pytest
from _pytest.monkeypatch import MonkeyPatch


def pytest_addoption(parser):
    _default_dump_file = "remote_urls.json"

    parser.addoption(
        "--intercept-remote", action="store_true", default=False,
        help="Intercepts outgoing connections requests.")
    parser.addoption(
        "--intercept-dump-file", action="store", nargs="?", type=str,
        metavar='dump filename', default=_default_dump_file,
        help=f"filepath where the intercepted requests are dumped. (default: {_default_dump_file})")


def pytest_configure(config):
    pytest._intercept_remote = config.getoption('--intercept-remote')
    pytest._intercept_dump_file = config.getoption('--intercept-dump-file')

    pytest._urllib_urls = []
    pytest._requests_urls = []
    pytest._sockets_hostport = []

    if not pytest._intercept_remote and config.option.verbose:
        print("Intercept outgoing requests disabled")


def dump():
    _urls = {
        'conn_urllib': pytest._urllib_urls,
        'conn_requests': pytest._requests_urls,
        'conn_socket': pytest._sockets_hostport}
    with open(pytest._intercept_dump_file, 'w') as fd:
        json.dump(_urls, fd)


@pytest.fixture(autouse=True, scope="session")
def intercept_remote_requests():

    def requests_mock(self, method, url, *args, **kwargs):
        full_url = f"{self.scheme}://{self.host}{url}"
        pytest._requests_urls.append(full_url)
        pytest.xfail(f"The test was about to {method} {full_url}")

    def socket_connect_mock(self, addr):
        self.close()
        host = addr[0]
        port = addr[1]
        pytest._sockets_hostport.append(addr)
        pytest.xfail(f"The test was about to connect to {host}:{port}")

    def urlopen_mock(self, http_class, req, **http_conn_args):
        pytest._urllib_urls.append(req.get_full_url())
        pytest.xfail(f"The test was about to call {req.get_full_url()}")

    if pytest._intercept_remote:
        _monkeypatch = MonkeyPatch()
        _monkeypatch.setattr(
            "urllib.request.AbstractHTTPHandler.do_open", urlopen_mock)
        _monkeypatch.setattr(
            "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock)
        _monkeypatch.setattr(
            "socket.socket.connect", socket_connect_mock)

    yield None

    if pytest._intercept_remote:
        dump()
        _monkeypatch.undo()

    return
