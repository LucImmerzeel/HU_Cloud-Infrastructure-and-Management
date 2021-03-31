from flask_oauthlib.client import OAuth

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    app_key='TWITTER'
)

app.config['TWITTER'] = dict(
    consumer_key='a random key',
    consumer_secret='a random secret',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)

oauth.init_app(app)