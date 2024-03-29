from main_module import capital
import yaml
import os
import pytest
import requests
import mock_capital.mock_server as test_http_server


@pytest.fixture()
def setup_mock(monkeypatch):
    # store a reference to the old get method
    monkeypatch.setattr(requests, "get", test_http_server.mocked_get)
    monkeypatch.setattr(requests, "post", test_http_server.mocked_post)
    monkeypatch.setattr(requests, "delete", test_http_server.mocked_get)


def setup():
    api_key = None
    password = None
    identifier = None
    if not os.path.exists("config.yaml"):
        print("No config file Probably Runner")
        assert os.environ.get("CAPITAL_API_TOKEN") is not None
        api_key = os.environ.get("CAPITAL_API_TOKEN")
        password = os.environ.get("CAPITAL_PASSWORD")
        identifier = os.environ.get("CAPITAL_IDENTIFIER")
        return api_key, password, identifier

    else:
        with open("config.yaml", "r") as file:
            conf = yaml.safe_load(file)
            assert conf is not None
            assert conf["capital"] is not None

            api_key = conf["capital"]["api_key"]
            password = conf["capital"]["password"]
            identifier = conf["capital"]["identifier"]
            return api_key, password, identifier


def test__server_time(setup_mock):
    res = capital.server_time(True)
    assert res is not None
    assert res.status_code == 200

    js = res.json()
    assert js is not None


def test__ping(setup_mock):
    security, cst = setup_session()
    assert security == "test_token"
    assert cst == "test"

    res = capital.ping(security, cst)
    assert res is not None
    assert res.status_code == 200

    data = res.json()
    assert data is not None


def setup_session():
    api_key, password, identifier = setup()
    assert api_key is not None
    assert password is not None
    assert identifier is not None
    _, _, security, cst = capital.create_session(
        api_key, password, identifier, demo=True
    )
    return security, cst


def test__create_session(setup_mock):
    api_key, password, identifier = setup()
    assert api_key is not None
    assert password is not None
    assert identifier is not None

    data, headers, security, cst = capital.create_session(
        api_key, password, identifier, demo=True
    )

    assert data is not None
    assert headers is not None
    assert security is not None
    assert cst is not None


def test__download(setup_mock):
    security, cst = setup_session()

    data = capital.download(
        "AAPL",
        security,
        cst,
        "DAY",
        start_date="2023-01-01T01:01:00",
        end_date="2023-05-01T01:01:00",
    )

    assert data is not None
    df, changed = capital.convert_download(data)

    assert df.empty is False
    assert df.index.size >= 10

    assert changed.empty is False
    assert df.columns.size == 9
    assert changed["Open"].empty is False


def test__get_positions(setup_mock):
    security, cst = setup_session()
    positions = capital.get_positions(security, cst)
    assert len(positions) == 2
    assert positions[0].symbol == "NATURALGAS"
    assert positions[1].symbol == "US500"


def test__log_out(setup_mock):
    security, cst = setup_session()
    res = capital.log_out(security, cst)
    assert res is not None
    assert res.status_code == 200

    data = res.json()
    assert data is not None
    assert data != ""


def test__set_positions(setup_mock):
    security, cst = setup_session()
    res = capital.set_positions("SILVER", 1, 20, 27, security, cst)
    assert res is not None
    assert res.status_code == 200

    answer = res.json()
    assert answer is not None
    print(answer)
    assert answer["dealReference"] is not None
