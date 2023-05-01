import http.client

CAPITAL_BACKEND = "api-capital.backend-capital.com"
CAPITAL_BACKEND_DEMO = "demo-api-capital.backend-capital.com"

def _getConnection(demo = True):
    if demo:
        return http.client.HTTPSConnection(CAPITAL_BACKEND_DEMO)
    else:
        return http.client.HTTPSConnection(CAPITAL_BACKEND)

def capitalPing(security_token, cst_token, demo = True):
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

def capitalServerTime(demo = True):
    conn = _getConnection(demo)
    payload = ''
    headers = {}
    conn.request("GET", "/api/v1/time", payload, headers)
    res = conn.getresponse()
    return res

def capitalDownload(symbol, token, cst, period, interval, security_token, cst_token, demo = True):
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
    print(data.decode("utf-8"))

def capitalCreateSession(security_token, demo = True):
    conn = http.client.HTTPSConnection("api-capital.backend-capital.com")
    payload = ''
    headers = {
      'X-CAP-API-KEY': security_token
    }
    conn.request("GET", "/api/v1/session/encryptionKey", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))