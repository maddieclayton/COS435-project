import json
import sys
import math

import re

import config
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


class Query(object):

    def __init__(self, query_string):
        self._query_string = query_string
        self._result_filename = None

    def run(self):
        """
        Run the actual query.
        Once this method is finished use the get_result_article() method to get the HTML of the resulting article.
        """
        with open("keys", 'r') as k:
            keys_file_content = k.read()

        keys = json.loads(keys_file_content)

        # Filter the query.
        query_string = self._query_string
        p = re.compile('\[[0-9]*?\]|\'s|/|\.|\(|\)|,|\"|\'|−|;|\[|\]|\*|:|~|\?|!|#|@')
        li = p.findall(query_string)
        for instance in li:
            query_string = query_string.replace(instance, '')
        query_words = query_string.split()
        print("Query words before processing: %s" % query_words)
        query_words = [word.lower() for word in query_words]
        sw = stopwords.words('english')
        query_words = filter(lambda x: x not in sw, query_words)

        # Apply stemming
        stemmer = PorterStemmer()
        query_words = map(lambda x: stemmer.stem(x), query_words)

        # print("Query words after processing: %s" % list(query_words))

        score_dict = {}
        for word in query_words:
            if len(word) > 2 and word in keys:
                path = "output/" + word + ".json"
                with open(path, 'r') as f:
                    dic_file_content = f.read()
                dic_entries = json.loads(dic_file_content)

                # Let's calculate the weight for that term. Weight is how important that term is in relation to the
                # whole collection
                factor = float(config.Config.collection_size) / float(len(dic_entries))
                weight = math.log10(factor)

                document_term_scores = {}
                # Very basic approach. Just use the weights as counts multiplied by query term weight.
                for entry in dic_entries:
                    doc = entry['filename']
                    if doc not in document_term_scores:
                        document_term_scores[doc] = 0

                    # Weight of the term in the document times our term weight (TF-IDF).
                    # We then normalize by the length of the file.
                    # dividend = math.log10(float(entry['filelength']))
                    # if dividend <= 0:
                        # dividend = 1
                    # document_term_scores[doc] += (entry['weight'] * weight) / dividend
                    document_term_scores[doc] += (entry['weight'] * weight)

                # Merge with overall score dict.
                for k in document_term_scores.keys():
                    if k not in score_dict:
                        score_dict[k] = 0

                    score_dict[k] += document_term_scores[k]

        if len(score_dict) > 0:
            result = max(score_dict, key=score_dict.get)
            self._result_filename = result

    def get_result_article(self):
        """
        :return: The html of the article that matches the query the best. If there is no result this will return None
        """
        if self._result_filename is not None:
            data_folder = config.Config.source_data_folder
            with open(data_folder + '/%s' % self._result_filename, 'r') as f:
                html = f.read()

            return html
        else:
            return None

    def get_result_filename(self):
        # Returns the filename of the article that was found to be most relevant.
        return self._result_filename


if __name__ == '__main__':
    query = Query(sys.argv[1])
    query.run()
    print(query.get_result_article())
