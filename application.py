from itertools import count
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from send_email import send_email
from sqlalchemy.sql import func
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

application = Flask(__name__)
application.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(application)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


#A class which database model will be its object
application.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgre1234@localhost/age_collector'
db=SQLAlchemy(application)

class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer, primary_key=True)
    email_=db.Column(db.String(120), unique=True)
    age_=db.Column(db.Integer)

    def __init__(self, email_, age_):
        self.email_=email_
        self.age_=age_

@application.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@application.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/index")

@application.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@application.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@application.route("/index")
def index():
    return render_template("index.html")

@application.route("/success",methods=['POST'])
def success():
    if request.method == 'POST':
        email=request.form["email_name"]
        age = request.form["age_name"]
        
        if db.session.query(Data).filter(Data.email_==email).count()==0:
            data=Data(email,age)
            db.session.add(data)
            db.session.commit()
            avg_age=db.session.query(func.avg(Data.age_)).scalar()
            avg_age=round(avg_age,1)
            count=db.session.query(Data.age_).count() 
            send_email(email,age,avg_age,count)
            return render_template("success.html")
        return render_template("index.html", 
        text="Seems like we've got something from the email address already!")

if __name__ == '__main__':
    application.debug=True
    application.run(host="0.0.0.0", port=env.get("PORT", 3000))
