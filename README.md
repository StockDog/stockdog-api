[![Build Status](https://travis-ci.org/sshaul/StockDog.svg?branch=master)](https://travis-ci.org/sshaul/StockDog)

![Stockdog](https://github.com/sshaul/StockDog/blob/master/Assets/logoColor.png)
## Learn to invest while competing with friends!

### Our Mission
> Investing is a useful life skill valuable to all young adults. However, to learn how to invest, young adults require knowledge of the market, sufficient capital, and a driving motivator. There exist classes that teach the ropes of the stock market, but there is no denying practice is the best educator. Young adults haven’t had a chance to earn enough money to expend on the stock market. Lastly, even though there exist applications with virtual money for users to practice investing, they lack the proper motivation to keep users engaged. We hope to solve these problems to allow young adults to get acquainted with the market in a captivating fashion.


### REST API Definition
It can be found [here](https://stockdog.gitbook.io/project/rest-api).


### Running locally
1. Set up mysql on your local machine and create a new user.
- If you want testing to work out of the box, you must set up the following:
    - user: sduser
    - pass: sdpass
    - host: localhost
    - database: StockDog
1. Create a `.env` file in the root and follow the format laid out in `.env.example`. The database name should be `StockDog`.
1. Run `mysql -u<the user you created> -p < db/init.sql`.
1. Run `pipenv install`. (`brew install pipenv` if you do not have pipenv.)
1. Run `pipenv run python3 app.py`.
1. Test that everything is working by running `curl localhost:5005`.

### Running tests
1. `pipenv shell`
1. `cd tests`
1. `python3 Runner.py`
1. When finished `cd ..` and `<cntrl + d>`.

### Deploying
1. Deploying is done through Heroku and is set up to auto-deploy on merge with `master`.