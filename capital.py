import http.client
import json
import pandas as pd


CAPITAL_BACKEND = "api-capital.backend-capital.com"
CAPITAL_BACKEND_DEMO = "demo-api-capital.backend-capital.com"

def _getConnection(demo = True):
    if demo:
        return http.client.HTTPSConnection(CAPITAL_BACKEND_DEMO)
    else:
        return http.client.HTTPSConnection(CAPITAL_BACKEND)

def capital_ping(security_token, cst_token, demo = True):
    conn = _getConnection(demo)
    payload = ''
    headers = {
      'X-SECURITY-TOKEN': security_token,
      'CST': cst_token
    }
    conn.request("GET", "/api/v1/ping", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

def server_time(demo = True):
    conn = _getConnection(demo)
    payload = ''
    headers = {}
    conn.request("GET", "/api/v1/time", payload, headers)
    res = conn.getresponse()
    return res

def download(symbol, security_token, cst_token, period, interval, demo = True):
    conn = _getConnection(demo)
    payload = ''
    headers = {
      'X-SECURITY-TOKEN': security_token,
      'CST': cst_token
    }
    url = "/api/v1/prices/" + symbol + "?resolution=" + str(period) + "&max=" + str(interval) 
    conn.request("GET", url, payload, headers)
    res = conn.getresponse()
    data = res.read()

    jdata = json.loads(data.decode("utf-8"))
    df = pd.DataFrame.from_dict(pd.json_normalize( jdata["prices"] ))
    return df

def get_encryption_key(security_token, demo = True):
    conn = _getConnection(demo)
    payload = ''
    headers = {
      'X-CAP-API-KEY': security_token
    }
    conn.request("GET", "/api/v1/session/encryptionKey", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data


def create_session(api_key,password,identifier, demo = True):
    conn = _getConnection(demo)
    payload = json.dumps({
      "identifier": identifier,
      "password": password
    })
    headers = {
      'X-CAP-API-KEY': api_key,
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    if res.getcode() == 200:
        data = res.read()
        security_token = res.headers["X-SECURITY-TOKEN"]
        cst = res.headers["CST"]
        return data, res.headers, security_token, cst
    raise ValueError