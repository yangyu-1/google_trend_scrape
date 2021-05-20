from pytrends.request import TrendReq
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

from _logger import get_logger
import logging
import argparse
from db_connect import mysql_conn

import urllib3
import urllib.request

urllib3.disable_warnings()
logger = get_logger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--kw_list", help="scrape keywords on amazon")

pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10, 25),
    retries=2,
    backoff_factor=0.1,
    requests_args={"verify": False},
)


def get_ip():
    external_ip = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    return external_ip


def trend_kw(keyword):
    logger.info(f"{keyword}- getting data from google trend")
    pytrends.build_payload([keyword], geo="US")
    df = pytrends.interest_over_time()

    if df.shape[0] > 1:
        logger.info(
            f"{keyword}- data return from google = {df.shape} - {df.columns.to_list()} - {min(df.index)} - {max(df.index)}"
        )
        if df.isPartial.dtypes == bool:
            df = df[df["isPartial"] == False]  # remove partial row
        elif df.isPartial.dtypes == np.object:
            df = df[df["isPartial"] == "False"]
        else:
            logger.info(f"{keyword}- isPartialReturn not bool nor text")
        df = df.iloc[:, :1]  # drop the isPartial Column
        df.columns = ["y"]  # Rename and add column
        df["keyword"] = keyword
        df["scrape_date"] = pd.Timestamp.now(tz="US/Pacific").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else:
        dict_ = {
            "date": pd.to_datetime("today").normalize(),
            "y": np.nan,
            "keyword": keyword,
        }
        logger.info(f"{keyword}- data return from google = {df.shape}")
        logger.info(f"{keyword}- Google Trend returns empty dataframe")
        df = pd.DataFrame([dict_])
        df.set_index("date", inplace=True)
        df["scrape_date"] = pd.Timestamp.now(tz="US/Pacific").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        logger.info(f"{keyword}- created no data df = {df}")
    return df


def add_ols(dataframe, ols_num):
    logger.info(f"{keyword}- Setting Slope")
    if dataframe.shape[0] > 1:
        logger.info(f"{keyword}- Data detected > 1. Calculating Slope")
        lr = LinearRegression()
        data = dataframe[-ols_num:].copy()
        data["x"] = np.arange(0, len(data))
        lr.fit(data[["x"]], data["y"])
        ypred = lr.predict(data[["x"]])
        m = lr.coef_[0]
        data["ols"] = ypred
        data["m"] = m
        data = data[["ols", "m"]]
    else:
        logger.info(f"{keyword}- Data detected <= 1. Setting Slope to Nan")
        data = dataframe.copy()
        m = np.nan
        data["ols"] = np.nan
        data["m"] = m
        data = data[["ols", "m"]]
    return data, m


def save_df(df):
    conn = mysql_conn()
    df.reset_index(inplace=True)
    df.to_sql(name="g_trend_data", con=conn, if_exists="append", index=False)
    logger.info(f"{keyword}- saving df {df.shape} to database")


if __name__ == "__main__":
    args = parser.parse_args()
    keywords = args.kw_list.split(",")
    ip = get_ip()
    for keyword in keywords:
        df = trend_kw(keyword)
        ols_df, m = add_ols(df, 26)
        mergedDf = df.merge(ols_df, left_index=True, right_index=True, how="left")
        mergedDf["ip"] = ip
        save_df(mergedDf)


# Better use for this website = scrape them for ideas, and do our own evaluation
# Trend hunter - stylus, trend bible, trend watching

# High star - extract keyword from reviews - document tagging -what keywords are in high stars that are unique
# Low star - extract keyword from reviews - document tagging
# from product to sub-product - NER

# Tuesday 10am
