import urllib.request

try:
    urllib.request.urlopen('https://www.google.com')
except:
    HAS_INTERNET = False
else:
    HAS_INTERNET = True

def assert_url(url):
    if not HAS_INTERNET:
        pytest.skip("Internet connection seems faulty")

    # TODO: On a 404 this will raise a urllib.error.HTTPError. It would be
    # nice to give some better output to the user here.
    resp = urllib.request.urlopen(url)
    assert resp.status == 200

