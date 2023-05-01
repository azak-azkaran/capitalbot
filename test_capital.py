import http.client
import capital 


def test__GetConnection():
    conn = capital._getConnection(True)
    assert conn != None
    assert conn.host == capital.CAPITAL_BACKEND_DEMO

def test__capitalServerTime():
    res = capital.capitalServerTime(True)
    assert res != None
    assert res.getcode() == 200
    data = res.read()
    print(data.decode("utf-8"))
    res.close()
    assert res.closed == True

def test__capitalCreateSession():
    res = capital.capitalCreateSession(security_token= , True)