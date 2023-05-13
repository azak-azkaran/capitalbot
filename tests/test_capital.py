import http.client
import capital
import yaml
import os


def test__set_connection():
    conn = capital._get_connection(True)
    assert conn != None
    assert conn.host == capital.CAPITAL_BACKEND_DEMO


def test__server_time():
    res = capital.server_time(True)
    assert res != None
    assert res.getcode() == 200
    data = res.read()
    print(data.decode("utf-8"))
    res.close()
    assert res.closed == True


def setup():
    api_key = None
    password = None
    identifier = None
    if not os.path.exists("config.yaml"):
        print("No config file Probably Runner")
        assert os.environ.get("CAPITAL_API_TOKEN") != None
        api_key = os.environ.get("CAPITAL_API_TOKEN")
        password = os.environ.get("CAPITAL_PASSWORD")
        identifier = os.environ.get("CAPITAL_IDENTIFIER")
        return api_key, password, identifier

    else:
        with open("config.yaml", "r") as file:
            conf = yaml.safe_load(file)
            assert conf != None
            assert conf["capital"] != None

            api_key = conf["capital"]["api_key"]
            password = conf["capital"]["password"]
            identifier = conf["capital"]["identifier"]
            return api_key, password, identifier


def setup_session():
    api_key, password, identifier = setup()
    assert api_key != None
    assert password != None
    assert identifier != None
    _, _, security, cst = capital.create_session(
        api_key, password, identifier, demo=True
    )
    return security, cst


def test__create_session():
    api_key, password, identifier = setup()
    assert api_key != None
    assert password != None
    assert identifier != None

    data, headers, security, cst = capital.create_session(
        api_key, password, identifier, demo=True
    )

    assert data != None
    assert headers != None
    assert security != None
    assert cst != None


def test__download():
    security, cst = setup_session()

    res = capital.download(
        "AAPL",
        security,
        cst,
        "DAY",
        start_date="2023-01-01T01:01:00",
        end_date="2023-05-01T01:01:00",
    )

    assert res != None
    df = capital.convert_download(res)

    assert df.empty == False
    assert df.index.size >= 10


def test__ping():
    security, cst = setup_session()
    res = capital.ping(security, cst)
    assert res != None

    data = res.read()
    assert data.getcode() == 200


def test__get_positions():
    security, cst = setup_session()
    res = capital.get_positions(security, cst)
    assert res != None

    data = res.read()
    assert data != None
    assert data.getcode() == 200
    assert data.decode("utf-8") != ""


def test__log_out():
    security, cst = setup_session()
    res = capital.log_out(security, cst)
    assert res != None

    data = res.read()
    assert data != None
    assert data.getcode() == 200
    assert data.decode("utf-8") != ""
