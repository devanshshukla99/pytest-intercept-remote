import json
import pytest
from _pytest.monkeypatch import MonkeyPatch


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


def pytest_addoption(parser):
    parser.addoption(
        "--intercept-remote", action="store_true", default=False,
        help="Intercepts outgoing connections requests.")
    parser.addoption(
        "--intercept-dump-file", action="store", nargs="?", type=str,
        metavar='dump', default=None,
        help="filepath at which intercepted requests are dumped.")
    parser.addini(
        'intercept_dump_file',
        'filepath at which intercepted requests are dumped. (overridden by --intercept-dump-file)',
        type="string", default="remote_urls.json")


def pytest_configure(config):
    pytest._urllib_urls = []
    pytest._requests_urls = []
    pytest._sockets_hostport = []
    pytest._intercept_remote = config.getoption('--intercept-remote')
    pytest._intercept_dump_file = config.getoption('--intercept-dump-file')
    if not pytest._intercept_dump_file:
        pytest._intercept_dump_file = str(config.getini('intercept_dump_file'))

    print(f"Dump: {pytest._intercept_dump_file}")
    if not pytest._intercept_remote and config.option.verbose:
        print("Intercept outgoing requests disabled")


@pytest.fixture(scope="session", autouse=True)
def intercept_remote():
    if not pytest._intercept_remote:
        yield
    else:
        mpatch = MonkeyPatch()
        mpatch.setattr(
            "urllib.request.AbstractHTTPHandler.do_open", urlopen_mock)
        mpatch.setattr(
            "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock)
        mpatch.setattr(
            "socket.socket.connect", socket_connect_mock)
        yield
        mpatch.undo()
        intercept_dump()


def intercept_dump():
    _urls = {
        'conn_urllib': pytest._urllib_urls,
        'conn_requests': pytest._requests_urls,
        'conn_socket': pytest._sockets_hostport}
    with open(pytest._intercept_dump_file, 'w') as fd:
        json.dump(_urls, fd)
