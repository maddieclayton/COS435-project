import logging
import re
import requests
from threading import Lock, Thread
from queue import Queue, Empty


class URLFrontier(object):
    """
    Container that keeps track of URLs we should visit in the future and URLs we have already visited.
    """

    seed_urls = {
        "https://en.wikipedia.org/wiki/Special:Random"  # Let's just start at some random place.
    }

    def __init__(self):
        # The set of visited urls.
        self._visited = set()
        self._visited_lock = Lock()

        # The queue that contains the urls we have to visit in the future.
        self._urls = Queue()
        for seed_url in URLFrontier.seed_urls:
            self._urls.put(seed_url)

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
        This method will block for at most 5 seconds if no URL is available. After 5 seconds it will return None.
        :return: A URL (string)
        """
        try:
            url = self._urls.get(timeout=5)
            return url
        except Empty as e:
            return None


class Parser(object):
    """
    Parses the content of one page.
    This parser does two things. It extracts URLs and the first paragraph (abstract).
    The URLs are added to the URLFrontier and the first paragraph is written to disk.
    """

    def __init__(self, url_frontier):
        """

        :type url_frontier: URLFrontier
        """
        self._url_regex = re.compile('href="/wiki/.*?"')
        self._url_frontier = url_frontier

        self._parse_lock = Lock()

    def parse(self, page_content):
        """
        Parses a page. This method returns immediately as it parses the contents asynchronously.
        :param page_content: The HTML content of the page that needs to be parsed.
        """

        # TODO: Parallelize this implementation according to method description.
        self._parse_lock.acquire()
        li = self._url_regex.findall(page_content)
        self._parse_lock.release()

        for s in li:
            url = 'https://en.wikipedia.org/' + s[7:-1]
            self._url_frontier.add_url(url)


class Fetcher(object):
    """
    The heart of the Crawler. Fetches data from urls obtained from the URL Frontier and forwards the content to the
    parser.
    """

    def __init__(self, thread_count):
        """
        :type thread_count: int The number of threads to use for fetching.
        """
        self._thread_count = thread_count
        self._logger = logging.getLogger('FetcherLogger')

        # Create all the objects we need.
        self._url_frontier = URLFrontier()
        self._parser = Parser(self._url_frontier)

    def start(self):
        # Create the threads and start them.
        threads = []
        for i in range(0, self._thread_count):
            thread = Thread(target=Fetcher._fetch_pages, args=(self._url_frontier, self._parser, self._logger))
            thread.start()
            threads.append(thread)

        # Let's wait for the threads to finish...
        for t in threads:
            t.join()

    @staticmethod
    def _fetch_pages(url_frontier, parser, logger):
        """
        Method fetches pages as long as url_frontier returns not visited pages.
        :type parser: Parser
        :type url_frontier: URLFrontier
        :param url_frontier: The URL frontier used to get new pages.
        :param parser: The parser to which the the page content should be sent.
        :return: None
        """

        # We work with a session to reuse TCP connections.
        session = requests.Session()

        while True:
            url = url_frontier.get_url()

            # Finish this method if we can't get any more urls...
            if url is None:
                return

            # Get that content.
            logger.info("Processing URL: %s" % url)
            response = session.get(url)
            parser.parse(response.text)


# Make this file callable!
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetcher = Fetcher(10)
    fetcher.start()
