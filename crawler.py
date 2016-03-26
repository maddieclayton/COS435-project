import logging
from threading import Lock
from queue import Queue


class URLFrontier(object):
    """
    Container that keeps track of URLs we should visit in the future and URLs we have already visited.
    """

    def __init__(self):
        # The set of visited urls.
        self._visited = set()
        self._visited_lock = Lock()

        # The queue that contains the urls we have to visit in the future.
        self._urls = Queue()

        # Used for URLFrontier logging.
        self._url_frontier_logger = logging.getLogger('URLFrontier')

    def add_url(self, url):
        """
        Add a URL to the frontier. If the URL was already visited, it will not be added.
        :param url: The URL to add
        """
        self._visited_lock.acquire()

        if url not in self._visited:
            self._visited.add(url)
            self._urls.put(url)
            self._url_frontier_logger.debug('New URL added: %s' % url)

        self._visited_lock.release()

    def get_url(self):
        """
        Get a URL that was not yet visited.
        :return: A URL (string)
        """
        return self._urls.get()
