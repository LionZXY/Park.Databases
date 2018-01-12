from . import methods

__all__ = ['methods', 'errors']
base_url = '/api'


def get_url(url):
    return base_url + url
