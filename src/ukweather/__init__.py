"""ukweather - climate and weather data for UK infrastructure modelling scenarios
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = 'unknown'
