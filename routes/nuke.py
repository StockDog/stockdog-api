from flask import Blueprint, request, Response, g

nuke_api = Blueprint('nuke_api', __name__)


@nuke_api.route('/api/v1.0/nuke', methods=['DELETE'])
def nuke():
   delete_tables([
       'User',
       'Portfolio',
       'Ticker',
       'Transaction',
       'Watchlist',
       'PortfolioHistory',
       'PortfolioItem',
       'League'
   ])

   return Response(status=200)


def delete_tables(tables):
   for table in tables:
        g.cursor.execute("DELETE FROM " + table)
        g.cursor.execute("ALTER TABLE " + table + " AUTO_INCREMENT=1")
