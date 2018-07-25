import logging

__version__ = 1.
__name__ = 'Oracle'
__all__ = ['NDTree', 'Oracle', 'OracleFunction', 'OraclePoint', 'OracleSTL']

# Logging configuration
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
