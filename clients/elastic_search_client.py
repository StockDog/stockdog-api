import elasticsearch
import os

def get_stocks_info(tickers):
    client = elasticsearch.Elasticsearch(hosts=[os.getenv("elasticsearch.host")])

    response = client.search({ "query": {"terms": {"Symbol.keyword": tickers}}})

    stocks = {}
    for hit in response["hits"]["hits"]:
        stocks[hit["_source"]["Symbol"]] = hit["_source"]

    return stocks