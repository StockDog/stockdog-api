[![Build Status](https://travis-ci.org/sshaul/StockDog.svg?branch=master)](https://travis-ci.org/sshaul/StockDog)

![Stockdog](https://github.com/sshaul/StockDog/blob/master/Assets/logoColor.png)
## Learn to invest while competing with friends!

### Our Mission
> Investing is a useful life skill valuable to all young adults. However, to learn how to invest, young adults require knowledge of the market, sufficient capital, and a driving motivator. There exist classes that teach the ropes of the stock market, but there is no denying practice is the best educator. Young adults haven’t had a chance to earn enough money to expend on the stock market. Lastly, even though there exist applications with virtual money for users to practice investing, they lack the proper motivation to keep users engaged. We hope to solve these problems to allow young adults to get acquainted with the market in a captivating fashion.


### REST API Definition
It can be found [here](https://stockdog.gitbook.io/project/rest-api).


### Running locally
Prerequisites: Python 3.6+, mysql, pip3, pipenv, elasticsearch, kibana (Use brew install to install any prerequisites)
1. Set up mysql on your local machine and create a new user with the following commands:
- `CREATE USER 'sduser'@'localhost' IDENTIFIED BY 'sdpass';`
- `GRANT ALL PRIVILEGES ON * . * TO 'sduser'@'localhost';` 
- `FLUSH PRIVILEGES;`
1. Set up [elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.7/brew.html):
- Once set up, go through the instructions for [StockAgg](https://github.com/asnewman/StockAgg) to populate the index used to gather stock information (name, sector, symbol, etc...).
- You may want to set up [Kibana](https://www.elastic.co/guide/en/kibana/current/brew.html) to make sure all the data is there.
1. Create a `.env` file in /stockdog-api and follow the format laid out in `.env.example`. For local setup, the following should be used:
- `db.database="StockDog"`
- `db.host="localhost"`
- `db.user="sduser"`
- `db.password="sdpass"`
- `elasticsearch.host="localhost:9200"`
1. From /stockdog-api, run `cd Scripts` and then run `./bootstrap.sh` (this will setup service dependencies and database)
1. Run `pipenv run python3 app.py`.
1. Test that everything is working by running `curl localhost:5005`.

### Running tests
1. `cd tests`
1. `pipenv run python3 Runner.py`

### Deploying
1. Deploying is done through Heroku and is set up to auto-deploy on merge with `master`.
