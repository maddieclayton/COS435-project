from flask import Flask
app = Flask(__name__)
app.debug = True
app.secret_key = 'A_REALLY_S3C43T_KEY'


@app.route("/<name>")
def hello(name):
    return "Hello World %s" % name


if __name__ == '__main__':
    app.run()