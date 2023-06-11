import http.client
import json
import pandas as pd
import os


CAPITAL_BACKEND = "api-capital.backend-capital.com"
CAPITAL_BACKEND_DEMO = "demo-api-capital.backend-capital.com"
CAPITAL_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _get_connection(demo=True):
    if demo:
        return http.client.HTTPSConnection(CAPITAL_BACKEND_DEMO)
    else:
        return http.client.HTTPSConnection(CAPITAL_BACKEND)


def _create_connection(security_token, cst_token, demo=True):
    conn = _get_connection(demo)
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst_token}
    return conn, headers


def ping(security_token, cst_token, demo=True):
    conn, headers = _create_connection(security_token, cst_token)
    payload = ""
    conn.request("GET", "/api/v1/ping", payload, headers)
    res = conn.getresponse()
    return res


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
):
    conn, headers = _create_connection(security_token, cst_token, demo)
    payload = ""
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

    conn.request("GET", url, payload, headers)
    res = conn.getresponse()

    if res.getcode() != 200:
        data = res.read()
        raise ValueError(data.decode("utf-8"))

    data = res.read()
    res.close()
    return data


def convert_download(
    data,
    save_to_file=False,
    symbol=None,
):
    jdata = json.loads(data.decode("utf-8"))
    df = pd.DataFrame.from_dict(pd.json_normalize(jdata["prices"]))

    df.index = df["snapshotTimeUTC"]
    df = df.drop(columns=["snapshotTimeUTC", "snapshotTime"])

    if save_to_file:
        path = os.path.join("./capital_" + symbol + ".json")
        df.to_json(path_or_buf=path)

    if df is None:
        raise ValueError("Could not convert download")

    changed = df.loc[
        :,
        [
            "openPrice.ask",
            "highPrice.ask",
            "lowPrice.ask",
            "closePrice.ask",
            "lastTradedVolume",
        ],
    ]
    changed = changed.rename(
        columns={
            "openPrice.ask": "Open",
            "highPrice.ask": "High",
            "lowPrice.ask": "Low",
            "closePrice.ask": "Close",
            "lastTradedVolume": "Volume",
        }
    )
    return df, changed


def create_session(api_key, password, identifier, demo=True):
    conn = _get_connection(demo)
    payload = json.dumps({"identifier": identifier, "password": password})
    headers = {"X-CAP-API-KEY": api_key, "Content-Type": "application/json"}

    conn.request("POST", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    data = res.read()
    if res.getcode() == 200:
        security_token = res.headers["X-SECURITY-TOKEN"]
        cst = res.headers["CST"]
        return data, res.headers, security_token, cst
    raise ValueError("ERROR: " + str(res.getcode()) + " : " + data.decode("utf-8"))


def log_out(security_token, cst, demo=True):
    conn, headers = _create_connection(security_token, cst, demo)
    payload = ""
    conn.request("DELETE", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    return res


def get_positions(security_token, cst, demo=True):
    conn, headers = _create_connection(security_token, cst, demo)
    payload = ""
    conn.request("GET", "/api/v1/positions", payload, headers)
    res = conn.getresponse()
    return res


def set_positions(security_token, cst, demo=True):
    conn, headers = _create_connection(security_token, cst, demo)
    payload = json.dumps(
        {
            "epic": "SILVER",
            "direction": "BUY",
            "size": 1,
            "guaranteedStop": True,
            "stopLevel": 20,
            "profitLevel": 27,
        }
    )
    headers["Content-Type"] = "application/json"
    conn.request("POST", "/api/v1/positions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def get_orders(security_token, cst, demo=True):
    conn, headers = _create_connection(security_token, cst, demo)
    payload = ""
    conn.request("GET", "/api/v1/workingorders", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def set_order(security_token, cst, demo=True):
    conn, headers = _create_connection(security_token, cst, demo)
    payload = json.dumps(
        {"epic": "SILVER", "direction": "BUY", "size": 1, "level": 20, "type": "LIMIT"}
    )
    headers["Content-Type"] = "application/json"

    conn.request("POST", "/api/v1/workingorders", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
