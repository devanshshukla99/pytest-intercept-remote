import json

import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser):
    parser.addoption("--intercept", action="store", nargs="?", type=str,
                     metavar='Intercept output file', default=None,
                     help="intercepts outgoing connections and dumps it to a file."
                     )


def pytest_configure(config):
    pytest._urllib_urls = []
    pytest._requests_urls = []
    pytest._sockets_ip = []
    config.getini('markers').append(
        'intercept: Intercept')


@pytest.fixture(scope='session')
def monkeypatch_session():
    m = MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(autouse=True, scope="session")
def no_http_requests(monkeypatch_session, pytestconfig):
    def requests_mock(self, method, url, *args, **kwargs):
        full_url = f"{self.scheme}://{self.host}{url}"
        pytest._requests_urls.append(full_url)
        raise RuntimeError(
            f"The test was about to {method} {full_url}"
        )

    def socket_connect_mock(self, addr):
        if len(addr) == 2:  # AF_INET4
            host, port = addr
        else:  # AF_INET6
            host, port, _, _ = addr

        pytest._sockets_ip.append(f"{host}:{port}")
        raise RuntimeError(
            f"The test was about to connect to {host}:{port}"
        )

    def urlopen_mock(self, http_class, req, **http_conn_args):
        pytest._urllib_urls.append(req.get_full_url())
        raise RuntimeError(
            f"The test was about to call {req.get_full_url()}"
        )

    if pytestconfig.getoption("intercept"):
        monkeypatch_session.setattr(
            "urllib.request.AbstractHTTPHandler.do_open", urlopen_mock
        )
        monkeypatch_session.setattr(
            "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock
        )
        monkeypatch_session.setattr(
            "socket.socket.connect", socket_connect_mock
        )


@pytest.fixture(scope='session', autouse=True)
def intercept_teardown(pytestconfig):
    yield None
    if pytestconfig.getoption("intercept"):
        intercept_file = pytestconfig.getoption("intercept")
        _urls = {'urllib': pytest._urllib_urls,
                 'requests': pytest._requests_urls,
                 'socket': pytest._sockets_ip,
                 }
        with open(intercept_file, "w") as fd:
            json.dump(_urls, fd)
            print("Dumped!")
    return
