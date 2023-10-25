import json
from main_module import capital


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


def _get_ping():
    return {"status": "OK"}


def _get_time():
    # Opening JSON file
    with open("./mock_capital/get_servertime.json", "r") as f:
        return json.load(f)
    assert False


def _get_session():
    with open("./mock_capital/get_session.json", "r") as f:
        return json.load(f)
    assert False


def _get_prices():
    with open("./mock_capital/get_prices.json", "r") as f:
        return json.load(f)
    assert False


def _get_positions():
    with open("./mock_capital/get_positions.json", "r") as f:
        return json.load(f)
    assert False


def _post_session():
    with open("./mock_capital/post_session.json", "r") as f:
        return json.load(f)
    assert False


def _post_positions():
    with open("./mock_capital/post_positions.json", "r") as f:
        return json.load(f)
    assert False


post_options = {
    "/api/v1/session": _post_session,
    "/api/v1/positions": _post_positions,
}

get_options = {
    "/api/v1/ping": _get_ping,
    "/api/v1/time": _get_time,
    "/api/v1/session": _get_session,
    "/api/v1/prices/AAPL": _get_prices,
    "/api/v1/positions": _get_positions,
}


def mocked_post(uri, *args, **kwargs):
    _, id = uri.split(capital.CAPITAL_BACKEND_DEMO, 1)
    id = id.split("?", 1)[0]
    returnjson = post_options[id]()

    # create a mocked requests object
    mock = MockResponse(returnjson, 200)
    return mock


def mocked_get(uri, *args, **kwargs):
    _, id = uri.split(capital.CAPITAL_BACKEND_DEMO, 1)
    id = id.split("?", 1)[0]
    returnjson = get_options[id]()

    # create a mocked requests object
    mock = MockResponse(returnjson, 200)
    return mock
