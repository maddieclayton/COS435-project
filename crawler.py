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
        "https://en.wikipedia.org/wiki/Main_Page",
    }

    def __init__(self):
        # The set of visited urls.
        self._visited = set()
        self._visited_lock = Lock()

        # Log all urls
        self._unique_url_file_handle = open('fetched_data/0_urls.txt', 'w')

        # The set of all urls that are either visited or todo.
        self._all_urls = set()
        self._all_urls_lock = Lock()

        # The queue that contains the urls we have to visit in the future.
        self._urls = Queue()
        for seed_url in URLFrontier.seed_urls:
            self._urls.put(seed_url)

        # Used for URLFrontier logging.
        self._url_frontier_logger = logging.getLogger('URLFrontier')



        self._wiki_url_filters = [
            re.compile('/File:'),
            re.compile('/Portal:'),
            re.compile('/Help:'),
            re.compile('/Talk:'),
            re.compile('/Wikipedia:'),
            re.compile('/Special:'),
            re.compile('/Template:'),
            re.compile('/User:'),
        ]

    def add_url(self, url):
        """
        Add a URL to the frontier. If the URL was already visited, it will not be added.
        :param url: The URL to add
        """

        if self.valid_wiki_url(url):
            self._all_urls_lock.acquire()

            if url not in self._all_urls:
                self._all_urls.add(url)
                self._urls.put(url)
                self._url_frontier_logger.debug('New URL added: %s' % url)
                # Add the line to the overview.
                self._unique_url_file_handle.write("%s\n" % url)

            self._all_urls_lock.release()

    def valid_wiki_url(self, url):
        """
        Check if the given url is a valid url of an article on wikipedia.
        """
        for regex in self._wiki_url_filters:
            if regex.search(url) is not None:
                return False

        return True

    def get_url(self):
        """
        Get a URL that was not yet visited.
        This method will block for at most 5 seconds if no URL is available. After 5 seconds it will return None.
        :return: A URL (string)
        """
        print("Visited: %d | Todo: %d" % (len(self._visited), self._urls.qsize()), end="\r")
        try:
            url = self._urls.get(timeout=5)
            self._visited_lock.acquire()
            self._visited.add(url)
            self._visited_lock.release()
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

        # Used to count the number of pages stored. Each page will be stored with this number as its name.
        self._page_counter = 0
        self._overview_file_handle = open('fetched_data/0_overview.txt', 'w')
        self._first_paragraph_regex = re.compile('<p>(.*?)</p>')

    def parse(self, page_content, page_url):
        """
        Parses a page. This method returns immediately as it parses the contents asynchronously.
        :param page_url: The URL from which this content was fetched.
        :param page_content: The HTML content of the page that needs to be parsed.
        """

        # TODO: Parallelize this implementation according to method description.
        self._parse_lock.acquire()
        li = self._url_regex.findall(page_content)
        self._parse_lock.release()

        for s in li:
            url = 'https://en.wikipedia.org/' + s[7:-1]
            self._url_frontier.add_url(url)

        # Save only the content of the first paragraph.
        self._save_first_paragraph(page_content, page_url)

    def _save_first_paragraph(self, page_content, page_url):
        # Add the line to the overview.
        self._overview_file_handle.write("%d\t%s\n" % (self._page_counter, page_url))

        # Extract the first paragraph
        result = self._first_paragraph_regex.search(page_content)
        if result is not None:
            with open('fetched_data/%d.html' % self._page_counter, 'w') as f:
                f.write(result.group(0))
            self._page_counter += 1


    def _save_page_content(self, page_content, page_url):
        # Add the line to the overview.
        self._overview_file_handle.write("%d\t%s" % (self._page_counter, page_url))
        # Write the whole content to a file.
        with open('fetched_data/%d.html' % self._page_counter, 'w') as f:
            f.write(page_content)
        self._page_counter += 1

    def cleanup(self):
        """
        Cleanup everything
        """
        self._overview_file_handle.close()


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

        self._cleanup()

    def _cleanup(self):
        """
        Cleans up all resources it used.
        """
        self._parser.cleanup()

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
            parser.parse(response.text, url)


# Make this file callable!
if __name__ == "__main__":
    logging.basicConfig(filename="processed.log", level=logging.INFO)
    fetcher = Fetcher(10)
    fetcher.start()
