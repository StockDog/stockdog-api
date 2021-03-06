import sys
from unittest import TestLoader, TestSuite, TextTestRunner

from authTests.PostUserTests import PostUserTests
from authTests.PostSessionTests import PostSessionTests
from authTests.DeleteSessionTests import DeleteSessionTests
from routesTests.GetChartsTests import GetChartsTests
from routesTests.PostDeletePortfolioTests import PostDeletePortfolioTests
from routesTests.PostTransactionTests import PostTransactionTests
from routesTests.GetPortfoliosTests import GetPortfoliosTests
from routesTests.GetPortfolioTests import GetPortfolioTests
from routesTests.PostLeagueTests import PostLeagueTests
from routesTests.GetStockTests import StockTests
from routesTests.GetLeagueTests import GetLeagueTests
from routesTests.PostDeleteWatchlistTests import PostWatchlistTests
from routesTests.GetWatchlistTests import GetWatchlistTests
from routesTests.GetLeagueInviteCodesTests import GetLeagueInviteCodesTests

if __name__ == '__main__':
    loader = TestLoader()
    suite = TestSuite(
        (
            loader.loadTestsFromTestCase(PostUserTests),
            loader.loadTestsFromTestCase(PostSessionTests),
            loader.loadTestsFromTestCase(DeleteSessionTests),
            loader.loadTestsFromTestCase(GetChartsTests),
            loader.loadTestsFromTestCase(PostDeletePortfolioTests),
            loader.loadTestsFromTestCase(PostTransactionTests),
            loader.loadTestsFromTestCase(GetPortfoliosTests),
            loader.loadTestsFromTestCase(GetPortfolioTests),
            loader.loadTestsFromTestCase(PostLeagueTests),
            loader.loadTestsFromTestCase(StockTests),
            loader.loadTestsFromTestCase(GetLeagueTests),
            loader.loadTestsFromTestCase(PostWatchlistTests),
            loader.loadTestsFromTestCase(GetWatchlistTests),
            loader.loadTestsFromTestCase(GetLeagueInviteCodesTests)
        )
    )
    runner = TextTestRunner()
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
