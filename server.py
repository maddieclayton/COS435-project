import random
import hashlib
import db

from twitter import TwitterAPI
from flask import Flask, render_template, request, session, abort

app = Flask(__name__)
app.debug = True
app.secret_key = 'A_REALLY_S3C43T_KEY'


def get_user_key():
    """
    Get the key of a user.
    """
    if "userkey" not in session:
        # Generate a new user key.
        userkey = hashlib.md5(str(random.randint(0, 10000)))
        session['userkey'] = userkey

    return session['userkey']


@app.route("/random-tweet")
def random_tweet():
    random_tweet = TwitterAPI.get_random_tweet()
    tweet_id = random_tweet['id']
    markup = TwitterAPI.get_tweet_markup(tweet_id)
    return render_template('tweet.html', tweet_html=markup)


@app.route('/rate-tweet/<tweet_id>')
def rate_tweet(tweet_id):
    """
    Get a rating for the given tweet id.
    The user is extracted from the session. The rating should be given
    in a GET parameter called 'rating'.
    Additionally the articles shown should be in a GET parameter called
    'articles'
    """

    # Let's collect all the data
    rating = request.args.get('rating', None)
    userkey = get_user_key()
    articles = request.args.get('articles', None)
    if rating is None or articles is None:
        abort(400)

    # TODO: Create an entry in the database.

    # Everything successful.
    return "", 201


if __name__ == '__main__':
    app.run()