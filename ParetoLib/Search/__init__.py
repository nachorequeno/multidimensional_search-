import logging

__version__ = 1.
__name__ = 'Search'
__all__ = ['CommonSearch', 'SeqSearch', 'ParSearch', 'Search', 'ResultSet', 'ParResultSet']

# Logging configuration
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
