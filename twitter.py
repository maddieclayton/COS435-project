import requests
import base64
import random

class TwitterAPI(object):
    """
    Load data from the twitter API
    """

    _consumer_key = "9M27ViON2F17phtSKKrAYSPvd"
    _consumer_secret = "qQ5JAWT0cKKy6eVeta7EA5ZCX0eq5lcsPyfPYRrH0Uh9O5mANR"

    _api_url = "https://api.twitter.com"

    # Tweets in New York
    _tweets_source_url = _api_url + "/1.1/search/tweets.json?geocode=40.7,-74.0,5mi&lang=en"

    # URLs
    _auth_url = _api_url + "/oauth2/token"

    # Application Auth token (Generated using get_app_access_token())
    _app_auth_token = 'AAAAAAAAAAAAAAAAAAAAABCwugAAAAAAhzrTYmxm0jdo0JtJKGy9nOtAWWE%3DE3Ay7ROEFVtGXEGfrpIeXlRNIVzHTHDdXvRc6W4ZiDdZMTa3tf'

    @staticmethod
    def get_app_access_token():
        # Prepare authorization header
        token_credentials = TwitterAPI._consumer_key + ":" + TwitterAPI._consumer_secret
        b64_encoded_credentials = base64.b64encode(bytes(token_credentials, 'UTF-8'))

        headers = {
            'Authorization': ('Basic %s' % b64_encoded_credentials.decode('UTF-8')),
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        body = {
            'grant_type': 'client_credentials'
        }
        s = requests.Session()
        request = requests.Request('POST', TwitterAPI._auth_url, headers,data=body)
        request = request.prepare()

        response = s.send(request)
        response_content = response.json()
        return response_content['access_token']

    @staticmethod
    def get_tweets():
        s = requests.Session()
        request = requests.Request('GET', TwitterAPI._tweets_source_url)
        request = request.prepare()
        request = TwitterAPI.add_authorization(request)
        response = s.send(request)
        return response.json()

    @staticmethod
    def get_random_tweet():
        tweets = TwitterAPI.get_tweets()
        tweets = tweets['statuses']
        return tweets[random.randint(0, len(tweets)-1)]

    @staticmethod
    def add_authorization(request):
        """
        :type request: requests.Request
        """
        request.headers['Authorization'] = 'Bearer %s' % TwitterAPI._app_auth_token
        return request


if __name__ == '__main__':
    # print("Access Token: %s" % TwitterAPI.get_app_access_token())
    print("Tweets: %s" % TwitterAPI.get_random_tweet())
