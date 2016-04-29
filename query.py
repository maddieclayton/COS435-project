import json
import sys
import csv
import config


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

        query_words = self._query_string.split()
        query_words = [word.lower() for word in query_words]
        score_dict = {}
        for word in query_words:
            if word in keys:
                path = "output/" + word + ".json"
                with open(path, 'r') as f:
                    dic_file_content = f.read()
                dic_entries = json.loads(dic_file_content)

                # Very basic approach. Just use the weights as counts.
                for entry in dic_entries:
                    doc = entry['filename']
                    if doc not in score_dict:
                        score_dict[doc] = 0

                    score_dict[doc] += entry['weight']

        print(score_dict)
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
