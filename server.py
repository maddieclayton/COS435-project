import twitter
from flask import Flask
app = Flask(__name__)
app.debug = True
app.secret_key = 'A_REALLY_S3C43T_KEY'


@app.route("/")
def hello():
    return "%s" % twitter.TwitterAPI.get_random_tweet()


if __name__ == '__main__':
    app.run()