import http.client
import json
import pandas as pd
import os


CAPITAL_BACKEND = "api-capital.backend-capital.com"
CAPITAL_BACKEND_DEMO = "demo-api-capital.backend-capital.com"


def _get_connection(demo=True):
    if demo:
        return http.client.HTTPSConnection(CAPITAL_BACKEND_DEMO)
    else:
        return http.client.HTTPSConnection(CAPITAL_BACKEND)


def capital_ping(security_token, cst_token, demo=True):
    conn = _get_connection(demo)
    payload = ""
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst_token}
    conn.request("GET", "/api/v1/ping", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def server_time(demo=True):
    conn = _get_connection(demo)
    payload = ""
    headers = {}
    conn.request("GET", "/api/v1/time", payload, headers)
    res = conn.getresponse()
    return res


def download(
    symbol,
    security_token,
    cst_token,
    period,
    interval="1000",
    demo=True,
    start_date=None,
    end_date=None,
    save_to_file=False,
):
    conn = _get_connection(demo)
    payload = ""
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst_token}
    url = (
        "/api/v1/prices/"
        + symbol
        + "?resolution="
        + str(period)
        + "&max="
        + str(interval)
    )
    if start_date != None:
        url += "&from=" + start_date
    if end_date != None:
        url += "&to=" + end_date

    print(url)
    conn.request("GET", url, payload, headers)
    res = conn.getresponse()
    data = res.read()

    if res.getcode() == 200:
        jdata = json.loads(data.decode("utf-8"))
        df = pd.DataFrame.from_dict(pd.json_normalize(jdata["prices"]))

        df.index = df["snapshotTimeUTC"]
        df = df.drop(columns=["snapshotTimeUTC", "snapshotTime"])

        if save_to_file:
            path = os.path.join("./capital_" + symbol + ".json")
            df.to_json(path_or_buf=path)
        return df

    elif res.getcode() == 400:
        print("Error: " + data.decode("utf-8"))
        return None
    else:
        print("Error: ")
        return None


def get_encryption_key(security_token, demo=True):
    conn = _get_connection(demo)
    payload = ""
    headers = {"X-CAP-API-KEY": security_token}
    conn.request("GET", "/api/v1/session/encryptionKey", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data


def create_session(api_key, password, identifier, demo=True):
    conn = _get_connection(demo)
    payload = json.dumps({"identifier": identifier, "password": password})
    headers = {"X-CAP-API-KEY": api_key, "Content-Type": "application/json"}
    conn.request("POST", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    if res.getcode() == 200:
        data = res.read()
        security_token = res.headers["X-SECURITY-TOKEN"]
        cst = res.headers["CST"]
        return data, res.headers, security_token, cst
    raise ValueError
