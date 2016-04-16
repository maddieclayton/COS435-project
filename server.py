from twitter import TwitterAPI
from flask import Flask, render_template
app = Flask(__name__)
app.debug = True
app.secret_key = 'A_REALLY_S3C43T_KEY'


@app.route("/random-tweet")
def random_tweet():
    random_tweet = TwitterAPI.get_random_tweet()
    tweet_id = random_tweet['id']
    markup = TwitterAPI.get_tweet_markup(tweet_id)
    return render_template('tweet.html', tweet_html=markup)


if __name__ == '__main__':
    app.run()