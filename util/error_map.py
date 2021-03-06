import simplejson as json


errors = {
   'unsupportedTicker': 'The stock ticker is either invalid or unsupported.',
   'iexUnavailable': 'Honestly, this probably means that iex is down lol.',
   'inviteCodeMismatch': "The invite code provided does not match any existing league",
   'missingInviteCode': 'Invite code was not provided to join league.',
   'unsupportedPortfolioGet': 'Please provide only the userId or only the leagueId.',
   'insufficientShares': 'Insufficient shares owned to make sale.',
   'nonexistentPortfolio': 'Portfolio does not exist.',
   'insufficientBuyPower': 'Insufficient buy power to make purchase.',
   'duplicateWatchlistItem': 'Ticker already exists in the watchlist of portfolio.',
   'duplicateEmail': 'User with email already exists.',
   'nonexistentUser': 'User does not exist.',
   'notLoggedIn': 'User must be logged in.',
   'passwordMismatch': 'Incorrect password for user.',
   'alphaVantageDown': 'AlphaVantage failed to respond',
   'endBeforeStart': 'The end date can not be before the start date',
   'leagueDurationTooLong': 'Leagues can last a maximum of 1 year',
   'invalidIexToken': 'The IEX token is invalid',
   'leagueNotFound': 'Given league ID does not exist',
   'tickerNotWatchlisted': 'The provided ticker is not on the watchlist of the given portfolio',
   'tickerAlreadyInWatchlist': 'The ticker is already watchlisted in this portfolio',
   'invalidAppTypeOrOs': 'appType must be either expo or standalone and os must be either android or ios',
   'wrongIssuerGoogle': 'Token iss is not from Google',
   'invalidAppleIdToken': 'There was something wrong with the Apple Id given',
   'duplicatePortfolio': 'There is a portfolio already registered to the user in the given league'
}
