import html.parser
import json
import os
import re
import sys
from nltk.corpus import stopwords
import csv


def create_index(data_dir):

    if not os.path.isdir('output'):
        os.makedirs('output')

    term_dict = {}
    files = os.listdir(data_dir)
    counter = 0
    for file in files:
        counter += 1
        print("%d/%d" % (counter, len(files)), end='\r')
        if '.html' in file:
            f = open(data_dir + '/' + file, 'r')
            readfile = f.read()

            # Parse the html
            parser = HTMLParser(filename=file)
            parser.feed(readfile)
            terms = parser.get_terms()

            # Merge these new terms with what we saw before.
            for term, entries in terms.items():
                if term not in term_dict:
                    term_dict[term] = []

                term_dict[term] += entries

    keys = []
    for key, entries in term_dict.items():
        # Filename needs to be checked. Some Filesystems limit filenames by 255 bytes.
        if len(key.encode('utf-8')) <= 255:
            # Create dictionaries and write them to the file.
            entry_dics = [e.to_dic() for e in entries]
            with open("output/" + key + ".json", "w") as f:
                f.write(json.dumps(entry_dics))
            keys.append(key)

    # Write the keys to a file.
    with open("keys", "w") as keys_file:
        keys_file.write(json.dumps(keys))


class DictionaryEntry(object):

    def __init__(self, weight, filename):
        self.weight = weight
        self.filename = filename
        self.filelength = 0

    def to_dic(self):
        """
        Returns a dictionary representation
        """
        return {
            'filename': self.filename,
            'weight': self.weight,
            'filelength': self.filelength,
        }

    def __str__(self):
        return '<File: %s (length: %d) weight: %d>' % (self.filename, self.filelength, self.weight)


class HTMLParser(html.parser.HTMLParser):
    """
    Parses HTML fragments to get counts and weights for terms.
    """

    def __init__(self, filename):
        """
        Initialize a new instance.
        :param filename: The name of the file from which the content that is later parsed comes.
        """
        super().__init__()

        self._filename = filename
        self._word_count = 0

        # The current weight.
        self._current_weight = 1

        # A mapping from tags to weights. When a term is within a tag, then the below given weight will be added to the
        # current weight.
        self._weights = {
            'b': 1,
            'a': 1,
        }

        # Stores all terms with its attributes
        self._terms_dict = {}

    def handle_starttag(self, tag, attrs):
        additional_weight = self._weights.get(tag, 0)
        self._current_weight += additional_weight

    def handle_endtag(self, tag):
        additional_weight = self._weights.get(tag, 0)
        self._current_weight -= additional_weight

    def handle_data(self, data):
        cleaned_data = self._clean_data(data)

        # Make the data to words...
        words = cleaned_data.split()
        words = [word.lower() for word in words]

        stops = stopwords.words('english')
        for word in words:
            if word not in stops:
                self._word_count += 1

                # Check if we encountered this word before. If not, create a new entry.
                if word not in self._terms_dict:
                    self._terms_dict[word] = []

                # Add a new dic entry for this occurence.
                dic_entry = DictionaryEntry(weight=self._current_weight, filename=self._filename)
                self._terms_dict[word].append(dic_entry)

    def get_terms(self):
        # Set the length of all words
        for word, entries in self._terms_dict.items():
            for e in entries:
                e.filelength = self._word_count

        # Let's return these dictionaries.
        return self._terms_dict

    def _clean_data(self, data):
        """
        Cleans the given data.
        """
        p = re.compile('\[[0-9]*?\]|\'s|/|\.|\(|\)|,|\"|\'|−|;|\[|\]|\*|:|~|\?|!')
        li = p.findall(data)
        for instance in li:
            data = data.replace(instance, '')

        return data


# If this script is called directly, run the indexer with the given folder.
if __name__ == '__main__':
    source_dir = sys.argv[1]
    create_index(source_dir)
