
def test_intercept_remote(testdir):
    testdir.copy_example('pytest_intercept_remote/plugin.py')

    # create a temporary conftest.py file
    testdir.makeconftest(
        """
        pytest_plugins = ['plugin']
        """
    )

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        import pytest
        from plugin import intercept_dump
        from urllib.request import urlopen
        import requests
        import socket
        def test_requests_urls():
            u = requests.get("https://www.python.org")
            assert u.status_code == 200

        def test_urllib_urls():
            u = urlopen("https://www.python.org/")
            assert u.status == 200

        def test_socket():
            s = socket.socket()
            assert s.connect(("www.python.org", 80)) is None

        def test_dump():
            intercept_dump()
            assert open(pytest._intercept_dump_file).read() == '{"conn_urllib": ["https://www.python.org/"], "conn_requests": ["https://www.python.org/"], "conn_socket": [["www.python.org", 80]]}'
        """
    )

    result = testdir.runpytest("--verbose", "--intercept-remote", "--intercept-dump-file=test_urls.json")
    result.assert_outcomes(xfailed=3, passed=1)