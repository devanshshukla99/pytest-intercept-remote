import pytest
from urllib.request import urlopen
import requests

def test_requests_urls():
    u = requests.get("http://www.google.com")
    assert u.status_code == 200

def test_urllib_urls():
    u = urlopen("http://www.google.com")
    assert u.status == 200

def test_fname():
    assert pytest._intercepted_file == None
