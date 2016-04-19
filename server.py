import json
import random
import hashlib
import db

from twitter import TwitterAPI
from flask import Flask, render_template, request, session, abort, send_from_directory

app = Flask(__name__)
app.debug = True
app.secret_key = 'A_REALLY_S3C43T_KEY'


def get_user_key():
    """
    Get the key of a user.
    """
    if "userkey" not in session:
        # Generate a new user key.
        userkey = hashlib.md5(str(random.randint(0, 10000)).encode('UTF-8'))
        session['userkey'] = userkey.hexdigest()

    return session['userkey']


@app.route("/random-tweet")
def random_tweet():
    random_tweet = TwitterAPI.get_random_tweet()
    tweet_id = random_tweet['id']

    # Store the random tweet
    with open('tweets/%d.json' % tweet_id, 'w') as f:
        f.write(json.dumps(random_tweet))

    markup = TwitterAPI.get_tweet_markup(tweet_id)
    parameters = {
        'tweet_html': markup,
        'ratings': [1, 2, 3, 4, 5],
        'tweet_id': tweet_id,
    }
    return render_template('tweet.html', **parameters)


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

    # Create an entry in the database.
    conn = db.connect()
    data = (tweet_id, rating, userkey, articles)
    conn.execute('INSERT INTO tweets (tweet_id, rating, user, topics) VALUES (?, ?, ?, ?)', data)
    conn.commit()
    conn.close()

    # Everything successful.
    return "", 201


@app.route('/static/<path:path>')
def serve_file(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()