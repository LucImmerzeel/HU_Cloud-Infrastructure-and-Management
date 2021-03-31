import os
import sys  # Use when calling other scripts

sys.path.append(os.path.realpath('.'))
sys.path.append(os.path.realpath('../dns-server'))

import json
import subprocess
import sqlite3
import base64

# Third party libraries
from flask import Flask, redirect, request, url_for, Response
# from flask_restful import Resource, Api
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests_oauthlib
import requests
from web_scripts.mongodb import to_db, from_db, replace_db, remove_db, update_db, all_from_db
from .db import init_db_command

# Internal imports
from user import User, Token

# Configuration
#INTERPRETER = os.environ.get("INTERPRETER", None)
#DNSSERVER = os.environ.get("DNSSERVER", None)
CERTFOLDER = os.environ.get("CERTFOLDER", None)
FLASK_URL = os.environ.get("FLASK_URL", None)

CLIENT_ID = os.environ.get("CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
AUTHORIZATION_BASE_URL = "https://app.simplelogin.io/oauth2/authorize"
TOKEN_URL = "https://app.simplelogin.io/oauth2/token"
USERINFO_URL = "https://app.simplelogin.io/oauth2/userinfo"

# This allows us to use a plain HTTP callback
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Start DNS
from web_scripts.restart_dns import restart_dns

restart_dns()

if __name__ == "__main__":
    app.run(ssl_context=(os.path.join(CERTFOLDER, "26417044_localhost.cert"),
                         os.path.join(CERTFOLDER, "26417044_localhost.key")), debug=True)


@login_manager.request_loader
def load_user_from_request(request):
    token = request.headers.get('Authorization')
    key = request.args.get('key')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        find = from_db("userdb", "users", {"token": token})

        if find is None:
            return None

        id = find["_id"]
        user_token = User(id_=id, name=token, email="", profile_pic="")
        return user_token

    # if token is not None:
    #     username, password = token.split(":")  # naive token
    #     user_entry = User.get(username)
    #     if (user_entry is not None):
    #         user = User()
    #         if (user.password == password):
    #             return user
    return None


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return """  <p>You must be logged in to access this content.</p>
                <a class="button" href="/">Back</a>""", 403


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("flask_portal"))
    else:
        return f""" <h1>Home</h1>
                    <h2>Welcome to the portal</h2>
                    <h3>Sign in here:</h3><br>
                    <a class="button" href="/google">Google Login</a><br>
                    <a class="button" href="/sso"   >SSO</a><br>
                    <a class="button" <!--style="display:none"--> href="https://{FLASK_URL}/api/v1.0/current?token=60c97f9275130e5b5ad1d72d">test token</a><br>
                    <a class="button" <!--style="display:none"--> href="https://{FLASK_URL}/api/v1.0/update?token=60c97f9275130e5b5ad1d72d&key=3717be6ea90134e896da74cf&fqdn=Test.LucImmerzeel.nl&ip=192.168.0.10">test token+key</a><br>
                """


@app.route("/google")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/sso")
def login_sso():
    simplelogin = requests_oauthlib.OAuth2Session(
        CLIENT_ID, redirect_uri=f"https://{FLASK_URL}/sso/callback"
    )
    authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)

    return redirect(authorization_url)


@app.route("/sso/callback")
def callback_sso():
    simplelogin = requests_oauthlib.OAuth2Session(CLIENT_ID)
    simplelogin.fetch_token(
        TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url
    )

    user_info = simplelogin.get(USERINFO_URL).json()

    # Create a user in our db with the information provided by Google
    user = User(
        id_=user_info["id"], name=user_info["name"], email=user_info["email"],
        profile_pic=str(user_info.get('avatar_url'))
    )

    # Doesn't exist? Add to database
    if not User.get(user_info["id"]):
        User.create(user_info["id"], user_info["name"], user_info["email"], str(user_info.get('avatar_url')))

    # Begin user session by logging the user in
    login_user(user)

    # Adding to MongoDB
    existingdata = from_db("userdb", "users", {"_id": str(user_info["id"])})
    #print(existingdata)
    if existingdata is None:
        to_db("userdb", "users", {"_id": str(user_info["id"]), 'name': user_info["name"],
                                  'email': user_info["email"], 'picture_location': user_info.get('avatar_url')})

    return redirect(url_for("flask_portal"))


@app.route("/google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user, remember=True)

    # Adding to MongoDB
    existingdata = from_db("userdb", "users", {"_id": str(unique_id)})
    print(existingdata)
    if existingdata is None:
        to_db("userdb", "users",
              {"_id": str(unique_id), 'name': users_name, 'email': users_email, 'picture_location': picture})

    # Send user to portal
    return redirect(url_for("flask_portal"))


@app.route("/portal", methods=['GET', 'POST'])
@login_required
def flask_portal():
    from web_scripts.portal import portal
    return portal()


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def flask_config_form():
    from web_scripts.config_form import config_form
    return config_form()


@app.route("/ddns", methods=['GET', 'POST'])
@login_required
def flask_config_ddns():
    from web_scripts.config_form import config_ddns
    return config_ddns()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/restart-dns")
@login_required
def flask_restart_dns():
    from web_scripts.restart_dns import restart_dns
    return restart_dns()


@app.route("/stop-dns")
@login_required
def flask_stop_dns():
    from web_scripts.stop_dns import stop_dns
    return stop_dns()


@app.route("/generate_new_token")
@login_required
def generate_new_token():
    import secrets
    update_db("userdb", "users", {"_id": str(current_user.id)}, {"$set": {"token": secrets.token_hex(12)}})
    return redirect(url_for("flask_config_form"))


@app.route("/generate_new_key")
@login_required
def generate_new_key():
    import secrets
    update_db("userdb", "users", {"_id": str(current_user.id)}, {"$set": {"apikey": secrets.token_hex(12)}})
    return redirect(url_for("flask_config_form"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# API ###########################################################
@app.route("/api/v1.0/current", methods=['GET', 'POST'])
@login_required
def flask_api_get():
    from web_scripts.api_response import api_response
    token = request.args.get('token')
    find = from_db("userdb", "users", {"token": token})
    #print(current_user.id)
    user_token = User(id_=find["_id"], name=token, email="", profile_pic="")
    login_user(user_token)
    return api_response()


@app.route("/api/v1.0/update", methods=['GET', 'POST'])
@login_required
def flask_api_update():
    from web_scripts.api_response import api_update
    token = request.args.get('token')
    key = request.args.get('key')
    find = from_db("userdb", "users", {"token": token})
    #print(current_user.id)
    if key == find["apikey"]:
        user_token = User(id_=find["_id"], name=token, email="", profile_pic="")
        login_user(user_token)
    else:
        return None
    return api_update()


@app.route("/api/v1.0/history", methods=['GET', 'POST'])
def flask_api_history():
    from web_scripts.api_response import api_history
    return api_history()


@app.route("/api/v1.0/delete", methods=['GET', 'POST'])
def api_delete():
    from bson.objectid import ObjectId

    record_fqdn = request.args.get('fqdn')
    user_id = request.args.get('id')
    id_tobe_removed = []
    for item in all_from_db("userdb", "records", {"FQDN": record_fqdn}):
        id_tobe_removed.append(ObjectId(item["_id"]))
    for id in id_tobe_removed:
        update_db("userdb", "users", {"_id": str(user_id)},  {"$pull": {"records": str(id)}})
        remove_db("userdb", "records", {"_id": str(id)})
    return redirect(url_for("flask_config_ddns"))
