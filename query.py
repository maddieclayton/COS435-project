import sys
import csv


class Query(object):

    def __init__(self, query_string):
        self._query_string = query_string
        self._result_filename = None

    def run(self):
        """
        Run the actual query.
        Once this method is finished use the get_result_article() method to get the HTML of the resulting article.
        """
        keys1 = open("keys")
        keys = []
        for key in keys1:
            keys.append(key[:-1])

        query_words = self._query_string.split()
        score_dict = {}
        for word in query_words:
            if word in keys:
                list_docs = csv.reader(open("output/" + word + ".csv"))
                list_docs1 = next(list_docs)
                for doc in list_docs1:
                    if doc in score_dict:
                        score_dict[doc] += 1 / len(list_docs1)
                    else:
                        score_dict[doc] = 1/len(list_docs1)

        result = max(score_dict, key=score_dict.get)
        self._result_filename = result

    def get_result_article(self):
        """
        :return: The html of the article that matches the query the best.
        """
        with open('fetched_data/%s' % self._result_filename, 'r') as f:
            html = f.read()

        return html


if __name__ == '__main__':
    query = Query(sys.argv[1])
    query.run()
    print(query.get_result_article())
