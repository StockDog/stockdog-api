[![Build Status](https://travis-ci.org/sshaul/StockDog.svg?branch=master)](https://travis-ci.org/sshaul/StockDog)

![Stockdog](https://github.com/sshaul/StockDog/blob/master/Assets/logoColor.png)
## Learn to invest while competing with friends!

### Our Mission
> Investing is a useful life skill valuable to all young adults. However, to learn how to invest, young adults require knowledge of the market, sufficient capital, and a driving motivator. There exist classes that teach the ropes of the stock market, but there is no denying practice is the best educator. Young adults haven’t had a chance to earn enough money to expend on the stock market. Lastly, even though there exist applications with virtual money for users to practice investing, they lack the proper motivation to keep users engaged. We hope to solve these problems to allow young adults to get acquainted with the market in a captivating fashion.


### REST API Definition
It can be found [here](https://stockdog.gitbook.io/project/rest-api).


### Running locally
1. Set up mysql on your local machine and create a new user.
1. Create a `config.json` file in Service/src and follow the format laid out in `config.json.example`. The database name should be `StockDog`.
3. Run `mysql -u<the user you created> -p < Service/db/init.sql`.
2. Run `source venv/bin/active`.
3. Run `python3 app.py`. If it fails, run `pip3 install -r -requirements.txt`. You may need to install pip3 if that fails.
4. Test that everything is working by running `curl localhost:5005`.