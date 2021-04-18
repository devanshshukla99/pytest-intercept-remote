import json

import pytest
from _pytest.monkeypatch import MonkeyPatch

@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser):
    parser.addoption("--intercept", action="store_true", default=False, help="intercepts outgoing connections.")
    # parser.addoption("--intercept-dump", action="store", default="url_records.json", help="file to dump intercepted urls.")


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
            f"3The test was about to {method} {full_url}"
        )

    def socket_connect_mock(self, addr):
        if len(addr) == 2:  # AF_INET4
            host, port = addr
        else:  # AF_INET6
            host, port, _, _ = addr

        pytest._sockets_ip.append(f"{host}:{port}")
        raise RuntimeError(
            f"2The test was about to connect to {host}:{port}"
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
def write_intercept_teardown(pytestconfig):
    yield None
    if pytestconfig.getoption("intercept"):
        _urls = {'urllib': pytest._urllib_urls,
                 'requests': pytest._requests_urls,
                 'socket': pytest._sockets_ip,
                 }
        with open("url_records.json", "w") as fd:
            json.dump(_urls, fd)
            print("Dumped!")
    return


# def pytest_unconfigure(monkeypatch_session):
#     """
#     Cleanup post-testing
#     """
#     monkeypatch_session.undo()
 

# def pytest_runtest_setup(item):
#     print("Entering!")
#     intercept = item.get_closest_marker('intercept')

#     intercept_config = item.config.getvalue("intercept")
#     if intercept is not None:
#         pytest.skip("need --remote-data option to run")
#     print("Exiting!")

# # pytest.main(['--setup-show', './plugin.py'], plugins=[FixtureRegPlugin()])
