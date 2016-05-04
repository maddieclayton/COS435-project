import datetime
import hashlib
import logging
import random
import re
import time
import os

import requests
from threading import Lock, Thread
from queue import Queue, Empty

output_dir = 'fetched_data_new'

class URLFrontier(object):
    """
    Container that keeps track of URLs we should visit in the future and URLs we have already visited.
    """

    seed_urls = {
        "wiki/New_York",
        "wiki/Hillary_Clinton",
        "wiki/Water",
        "wiki/Main_Page",
        "wiki/Technology",
    }

    def __init__(self):
        # The set of visited urls.
        self._visited_count = 0
        self._visited_lock = Lock()

        # Log all urls
        self._backqueue_logger = logging.getLogger('backqueue_size')

        # The set of all urls that are either visited or todo.
        self._all_urls_hashes = set()
        self._all_urls_lock = Lock()

        # The queue that contains the urls we have to visit in the future.
        self._urls = Queue()
        for seed_url in URLFrontier.seed_urls:
            self._urls.put(seed_url)

        self._wiki_url_filters = [
            re.compile('/File:'),
            re.compile('/Book:'),
            re.compile('/Portal:'),
            re.compile('/Help:'),
            re.compile('/Talk:'),
            re.compile('/Wikipedia:'),
            re.compile('/Wikipedia_talk:'),
            re.compile('/Special:'),
            re.compile('/Template:'),
            re.compile('/Template_talk:'),
            re.compile('/User:'),
            re.compile('/User_talk:'),
            re.compile('/Category:'),
            re.compile('/Lists_of_'),
            re.compile('/List_of_'),
            re.compile('/Timeline_of_'),
            re.compile('/History_of_'),
            re.compile('/films_of_'),
        ]

        # The maximum number of urls to hold in memory. Must be larger than 100000
        self._url_threshold = 200000

    def _clean_url(self, url):
        """
        Clean a URL. Removes anchors.
        :param url: The url to clean
        :return: The cleaned url
        """
        index = len(url)
        try:
            index = url.index('#')
        except ValueError:
            pass

        return url[:index]

    def add_url(self, url):
        """
        Add a URL to the frontier. If the URL was already visited, it will not be added.
        :param url: The URL to add
        """

        # Cleanup the url first.
        url = self._clean_url(url)

        if self.valid_wiki_url(url):
            self._all_urls_lock.acquire()

            # Compute the hash of the url. We only use the first 15 elements to save some more space.
            url_hash = hashlib.md5(url.encode('UTF-8')).hexdigest()
            url_hash = url_hash[:15]

            if url_hash not in self._all_urls_hashes:
                self._all_urls_hashes.add(url_hash)
                self._urls.put(url)

            self._all_urls_lock.release()

        # Check if we have too many URLs in memory. If yes, write them to a file for later retrieval.
        if self._urls.qsize() > self._url_threshold:
            self._all_urls_lock.acquire()
            with open(output_dir + '/temp_urls.txt', 'a') as f:
                for i in range(0, self._url_threshold - 100000):
                    try:
                        f.write(self._urls.get(False) + "\n")
                    except Empty:
                        pass
            self._all_urls_lock.release()

    def valid_wiki_url(self, url):
        """
        Check if the given url is a valid url of an article on wikipedia.
        :param url: The url that needs to be checked if it is valid.
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
        print("Visited: %d | Todo: %d | Total: %d" % (self._visited_count, self._urls.qsize(), len(self._all_urls_hashes)), end="\r")
        try:
            url = self._urls.get(timeout=5)
            self._visited_lock.acquire()
            self._visited_count += 1
            self._visited_lock.release()

            # Log the size of the back queue (# of visited and total number)
            self._backqueue_logger.info("%d\t%d", self._visited_count, len(self._all_urls_hashes))

            return 'https://en.wikipedia.org/' + url
        except Empty as e:
            # XXX: Need to add lock around temp_urls file. Might result in crasho otherwise if multiple try to read from it!
            # Maybe we have none left in the queue. Let's load some from disk.
            self._all_urls_lock.acquire()

            path = output_dir + '/temp_urls.txt'
            if not os.path.isfile(path):
                return None

            # Load from the file
            with open(path, 'r') as f:
                i = 0
                for line in f:
                    self._urls.put(line)

                    # Read a maximum number of lines
                    if i >= self._url_threshold - 100000:
                        break

            # Check if we read the complete file.
            if i < self._url_threshold - 100000:
                os.remove(path)

            self._all_urls_lock.release()

            # We should now have something in the queue. And if not, the recursive call will return None after
            # finding out that the temp_urls file doesn't exist.
            return self.get_url()


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
        self._url_frontier = url_frontier

        # Used to count the number of pages stored. Each page will be stored with this number as its name.
        self._page_counter = 0
        self._page_counter_lock = Lock()

        # The queue that contains (url, content) tuples that need to be processed.
        self._content_queue = Queue()

        # Start several threads that actually do the work.
        thread_count = 3
        self._threads = set()
        for i in range(0, thread_count):
            thread = ParserThread(i, self._content_queue, self._url_frontier)
            thread.start()
            self._threads.add(thread)

    def parse(self, page_content, page_url):
        """
        Parses a page. This method returns immediately as it parses the contents asynchronously.
        :param page_url: The URL from which this content was fetched.
        :param page_content: The HTML content of the page that needs to be parsed.
        """

        # Ensure content queue doesn't blow up!
        if self._content_queue.qsize() > 300:
            time.sleep(0.1)

        # Add to the queue and return immediately
        self._content_queue.put((page_url, page_content))



class ParserThread(Thread):
    """
    Thread that processes (page_url, page_content) tuples.
    """

    def __init__(self, thread_number, content_queue, url_frontier):
        super().__init__()
        self._overview_logger = logging.getLogger('overview')

        # The queue from which the content is fetched.
        self._content_queue = content_queue

        # URL Frontier to which new urls are added.
        self._url_frontier = url_frontier

        # Thread number together with page_counter identify a page when it is written to a file.
        self._thread_number = thread_number
        self._page_counter = 0

        # Several regexes
        self._url_regex = re.compile('href="/wiki/.*?"')
        self._first_paragraph_regex = re.compile('<p>(.*?)</p>')

    def run(self):
        while True:
            (page_url, page_content) = self._content_queue.get()

            # Find all the links
            li = self._url_regex.findall(page_content)
            for s in li:
                url = s[7:-1]  # url looks like: 'wiki/...'
                self._url_frontier.add_url(url)

            # Save only the content of the first paragraph.
            self._save_first_paragraph(page_content, page_url)

    def _save_first_paragraph(self, page_content, page_url):

        # Add the line to the overview.
        self._overview_logger.info("%d-%d\t%s\n", self._thread_number, self._page_counter, page_url)

        # Extract the first paragraph
        result = self._first_paragraph_regex.search(page_content)
        if result is not None:
            first_paragraph_content = result.group(0)
            # Make sure we ignore the "may/can refer to:" pages.
            if " refer to:" not in first_paragraph_content.lower():
                with open(output_dir + '/%d-%d.html' % (self._thread_number, self._page_counter), 'w') as f:
                    f.write(first_paragraph_content)
                self._page_counter += 1


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
        self._logger = logging.getLogger('processed_urls')
        self._network_logger = logging.getLogger('network_log')

        # Create all the objects we need.
        self._url_frontier = URLFrontier()
        self._parser = Parser(self._url_frontier)

    def start(self):
        # Create the threads and start them.
        threads = []
        for i in range(0, self._thread_count):
            thread = Thread(target=Fetcher._fetch_pages, args=(self._url_frontier, self._parser, self._logger, self._network_logger))
            thread.start()
            threads.append(thread)

        # Let's wait for the threads to finish...
        for t in threads:
            t.join()

        print("Finished Crawling at %s" % datetime.datetime.now())

    @staticmethod
    def _fetch_pages(url_frontier, parser, logger, network_logger):
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
            logger.info(url)

            # Try to get the content of that url and parse it.
            try:
                start = time.time()
                response = session.get(url)
                network_logger.info("%f", time.time() - start)

                parser.parse(response.text, response.url)
            except ConnectionError:
                print("Failed to get URL: %s" % url)


def setup_logging():
    loggers = [
        ("overview", "0_overview.log"),  # Number and URL
        ("processed_urls", "0_processed_urls.log"),  # All URLs that have been processed so far
        ("backqueue_size", "0_backqueue_size.log"),  # Number and URL
        ("network_log", "0_network_log.log"),  # Time to fetch pages
    ]

    for (name, filename) in loggers:
        l = logging.getLogger(name)
        l.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s : %(message)s')
        file_handler = logging.FileHandler(filename=output_dir + '/' + filename, mode='w')
        file_handler.setFormatter(formatter)
        l.addHandler(file_handler)


# Make this file callable!
if __name__ == "__main__":
    setup_logging()

    # Start fetching data!
    fetcher = Fetcher(10)
    fetcher.start()
