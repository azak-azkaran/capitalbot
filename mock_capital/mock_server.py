import json
import capital


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.closed = False
        self.headers = {
            "X-SECURITY-TOKEN": "test_token",
            "CST": "test",
        }

    def json(self):
        return self.json_data

    def read(self):
        return json.dumps(self.json_data).encode("utf-8")

    def close(self):
        self.closed = True
        return self.closed


def ping():
    return {"status": "OK"}


def time():
    # Opening JSON file
    with open("./mock_capital/get_servertime.json", "r") as f:
        return json.load(f)
    assert False


def session():
    with open("./mock_capital/post_session.json", "r") as f:
        return json.load(f)
    assert False


def prices():
    with open("./mock_capital/get_prices.json", "r") as f:
        return json.load(f)
    assert False


def positions():
    with open("./mock_capital/get_positions.json", "r") as f:
        return json.load(f)
    assert False


options = {
    "/api/v1/ping": ping,
    "/api/v1/time": time,
    "/api/v1/session": session,
    "/api/v1/prices/AAPL": prices,
    "/api/v1/positions": positions,
}


def mocked_get(uri, *args, **kwargs):
    """A method replacing Requests.get
    Returns either a mocked response object (with json method)
    or the default response object if the uri doesn't match
    one of those that have been supplied.
    """
    _, id = uri.split(capital.CAPITAL_BACKEND_DEMO, 1)
    id = id.split("?", 1)[0]
    returnjson = options[id]()

    # create a mocked requests object
    mock = MockResponse(returnjson, 200)
    return mock
