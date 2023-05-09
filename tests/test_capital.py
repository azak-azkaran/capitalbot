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
        api_key = os.environ.get("CAPITAL_API_TOKEN")
        password = os.environ.get("CAPITAL_PASSWORD")
        identifier = os.environ.get("CAPITAL_IDENTIFIER")

    else:
        with open("config.yaml", "r") as file:
            conf = yaml.safe_load(file)
            assert conf != None
            assert conf["capital"] != None

            api_key = conf["capital"]["api_key"]
            password = conf["capital"]["password"]
            identifier = conf["capital"]["identifier"]
    return api_key, password, identifier


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
    api_key, password, identifier = setup()
    assert api_key != None
    assert password != None
    assert identifier != None
    data, headers, security, cst = capital.create_session(
        api_key, password, identifier, demo=True
    )

    df = capital.download(
        "AAPL",
        security,
        cst,
        "DAY",
        start_date="2023-01-01T01:01:00",
        end_date="2023-05-01T01:01:00",
    )

    assert df.empty == False
    assert df.index.size >= 10
