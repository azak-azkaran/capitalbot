import http.client
import capital 
import yaml


def test__GetConnection():
    conn = capital._getConnection(True)
    assert conn != None
    assert conn.host == capital.CAPITAL_BACKEND_DEMO

def test__serverTime():
    res = capital.serverTime(True)
    assert res != None
    assert res.getcode() == 200
    data = res.read()
    print(data.decode("utf-8"))
    res.close()
    assert res.closed == True

def test__createSession():
    with open('config.yaml', 'r') as file:
        conf = yaml.safe_load(file)
        assert conf != None
        assert conf["capital"] != None

        api_key = conf["capital"]["api_key"]
        password = conf["capital"]["password"]
        identifier = conf["capital"]["identifier"]
        assert api_key != None
        assert password != None
        assert identifier != None

        res,security,cst = capital.createSession(api_key,password,identifier, demo=True)