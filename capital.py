import http.client
import json
import os
import pandas as pd
import requests


CAPITAL_BACKEND = "api-capital.backend-capital.com"
CAPITAL_BACKEND_DEMO = "demo-api-capital.backend-capital.com"
CAPITAL_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _get_url(demo=True):
    if demo:
        return "https://" + CAPITAL_BACKEND_DEMO
    else:
        return "https://" + CAPITAL_BACKEND


def ping(security_token, cst_token, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst_token}
    res = requests.get(_get_url(demo) + "/api/v1/ping", headers=headers)
    return res


def server_time(demo=True):
    res = requests.get(_get_url(demo) + "/api/v1/time")
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
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst_token}
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

    res = requests.get(_get_url(demo) + url, payload, headers=headers)
    data = res.json()
    if res.status_code != 200:
        raise ValueError(str(data))
    return data


def convert_download(
    jdata,
    save_to_file=False,
    symbol=None,
):
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
    payload = json.dumps({"identifier": identifier, "password": password})
    headers = {"X-CAP-API-KEY": api_key, "Content-Type": "application/json"}

    res = requests.post(_get_url(demo) + "/api/v1/session", payload, headers=headers)
    data = res.json()
    if res.status_code == requests.codes.ok:
        security_token = res.headers["X-SECURITY-TOKEN"]
        cst = res.headers["CST"]
        return data, res.headers, security_token, cst
    raise ValueError("ERROR: " + str(res.status_code) + " : " + str(data))


def log_out(security_token, cst, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst}
    res = requests.delete(_get_url(demo) + "/api/v1/session", headers=headers)
    return res


def get_positions(security_token, cst, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst}
    res = requests.get(_get_url(demo) + "/api/v1/positions", headers=headers)

    jdata = res.json()

    df = pd.DataFrame.from_dict(pd.json_normalize(jdata))

    return df


def set_positions(security_token, cst, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst}
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
    res = requests.post(_get_url(demo) + "/api/v1/positions", payload, headers=headers)
    print(res.json())


def get_orders(security_token, cst, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst}
    res = requests.get(_get_url(demo) + "/api/v1/workingorders", headers=headers)
    print(res.json())


def set_order(security_token, cst, demo=True):
    headers = {"X-SECURITY-TOKEN": security_token, "CST": cst}
    payload = json.dumps(
        {"epic": "SILVER", "direction": "BUY", "size": 1, "level": 20, "type": "LIMIT"}
    )
    headers["Content-Type"] = "application/json"

    res = requests.post(
        _get_url(demo) + "/api/v1/workingorders", payload, headers=headers
    )
    print(res.json())
