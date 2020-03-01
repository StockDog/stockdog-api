import elasticsearch
import os
from flask import g
import json 

def get_stocks_info(tickers):
    client = elasticsearch.Elasticsearch(hosts=[os.getenv("elasticsearch.host")])

    response = client.search({ "query": {"terms": {"Symbol.keyword": tickers}}})

    stocks = {}
    for hit in response["hits"]["hits"]:
        stocks[hit["_source"]["Symbol"]] = hit["_source"]

    g.log.info(f'Retrieved {tickers} from ElasticSearch')
    g.log.info(json.dumps(stocks))

    return stocks