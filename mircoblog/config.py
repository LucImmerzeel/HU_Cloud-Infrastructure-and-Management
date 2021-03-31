import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('smtp.strato.com')
    MAIL_PORT = int(os.environ.get('465') or 25)
    MAIL_USE_TLS = os.environ.get('1') is not None
    MAIL_USERNAME = os.environ.get('spam@spam.lucimmerzeel.nl')
    MAIL_PASSWORD = os.environ.get('Wni75#4B0R8CyPkP')
    ADMINS = ['spam@spam.lucimmerzeel.nl', 'flask@spam.lucimmerzeel.nl']
    POSTS_PER_PAGE = 25
