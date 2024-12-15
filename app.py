from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import json
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime as dt
from iformat import iprint
from math import prod
import pytz

# dt.datetime.now(dt.timezone.utc)

app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    UserId:int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username:str = db.Column(db.String(80), unique=True, nullable=False)
    Password:str = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return self.UserId

class Bet(db.Model):
    BetId:int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Category:str = db.Column(db.String(80), nullable=False)
    Details:str = db.Column(db.String(200), nullable=False)
    Odds:float = db.Column(db.Float, nullable=False)
    Success:bool = db.Column(db.Boolean, nullable=True)

class Parlay(db.Model):
    ParlayId:int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Datetime:dt.datetime = db.Column(db.DateTime, nullable=False)
    UserId:int = db.Column(db.Integer, db.ForeignKey('user.UserId'), nullable=False)
    MatchupId:int = db.Column(db.Integer, db.ForeignKey('matchup.MatchupId'), nullable=False)
    Wager:float = db.Column(db.Float, nullable=False)
    BetId1:int = db.Column(db.Integer, db.ForeignKey('bet.BetId'), nullable=False)
    BetId2:int = db.Column(db.Integer, db.ForeignKey('bet.BetId'), nullable=False)
    BetId3:int = db.Column(db.Integer, db.ForeignKey('bet.BetId'), nullable=False)

class Matchup(db.Model):
    MatchupId:int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Datetime:dt.datetime = db.Column(db.DateTime, nullable=False)
    Home:str = db.Column(db.String(80), nullable=False)
    Away:str = db.Column(db.String(80), nullable=False)

def am_to_dec(am_odds):
    if am_odds > 0:
        return 1 + (am_odds / 100)
    else:
        return 1 + (100 / abs(am_odds))

def dec_to_am(dec_odds):
    if dec_odds > 2:
        return round((dec_odds - 1) * 100)
    else:
        return round(-100 / (dec_odds - 1))

def calculate_dec_odds(odds):
    return prod([am_to_dec(o) for o in odds])

def format_am_odds(odds):
    return f"{('+' if odds > 0 else '')}{round(odds)}"

def calc_parlay_info(raw_odds, wager):
    dec_odds = calculate_dec_odds(raw_odds)
    odds = format_am_odds(dec_to_am(dec_odds))
    percent = round((1 / dec_odds) * 100, 1)
    payout = round(wager * dec_odds, 2)
    win = payout - wager
    return dec_odds, odds, percent, payout, win

class DisplayableUsername:
    def __init__(self, user:User, current_user=None):
        self.id = user.UserId
        self.username = user.Username if user != current_user else "You"

class DisplayableMatchup:
    def __init__(self, matchup:Matchup):
        mst = pytz.timezone("US/Mountain")
        self.id = matchup.MatchupId
        self.date = matchup.Datetime.astimezone(mst).strftime("%m/%d/%Y")
        self.time = matchup.Datetime.astimezone(mst).strftime("%I:%M %p")
        self.home = matchup.Home
        self.away = matchup.Away

class DisplayableBet:
    def __init__(self, bet:Bet):
        self.id = bet.BetId
        self.category = bet.Category
        self.details = bet.Details
        self.raw_odds = bet.Odds
        self.odds = format_am_odds(bet.Odds)
        self.success = bet.Success

class DisplayableParlay:
    def __init__(self, parlay:Parlay, current_user=None):
        self.id = parlay.ParlayId
        self.user = DisplayableUsername(db.session.get(User, parlay.UserId), current_user)
        self.wager = parlay.Wager
        self.bets = [DisplayableBet(b) for b in db.session.query(Bet).filter(Bet.BetId.in_([parlay.BetId1, parlay.BetId2, parlay.BetId3])).all()]
        self.matchup = DisplayableMatchup(db.session.get(Matchup, parlay.MatchupId))
        self.dec_odds, self.odds, self.percent, self.payout, self.win = calc_parlay_info([b.raw_odds for b in self.bets], self.wager)
        self.success = None if None in (sl:=[b.success for b in self.bets]) else all(sl:=[b.success for b in self.bets])

    def __str__(self):
        return f"""
{self.user.username} bet {self.wager} on {self.matchup.home} vs {self.matchup.away} at {self.matchup.time} on {self.matchup.date}.
Bet 1: {self.bets[0].category} - {self.bets[0].details} ({self.bets[0].odds})
Bet 2: {self.bets[1].category} - {self.bets[1].details} ({self.bets[1].odds})
Bet 3: {self.bets[2].category} - {self.bets[2].details} ({self.bets[2].odds})
"""
    
    def __repr__(self):
        return self.__str__()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(UserId=user_id).first()

with app.app_context():
    db.create_all()

def sanitize(s):
    return s.replace("'", "").replace('"', "").replace(";", "")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = "".join(c for c in request.form.get("username").lower() if c.isalnum())
        password = request.form.get("password")

        if not user or not password:
            return render_template("login.html", error="Please fill out all the fields")

        user_record = User.query.filter_by(Username=user).first()

        if user_record:
            if not user_record.Password:
                user_record.Password = generate_password_hash(password)
                db.session.commit()
                flash("Your password was (re)set.", category="success")
            elif check_password_hash(user_record.Password, password):
                login_user(user_record)
                print(f"User {user} logged in.")
                return redirect(url_for("parlays"))
            else:
                return render_template("login.html", error="Incorrect password.\nIf you were creating a new account, this username is already taken.")
        elif sanitize(password) != password:
                return render_template("login.html", error="Passwords may not contain '\";.")
        else:
            new_user = User(Username=user, Password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            print(f"User {user} created.")
            flash(f"Account created with username {user}.", category="success")
            return redirect(url_for("parlays"))
    else:
        return render_template("login.html")

@app.route("/parlays")
def parlays():
    user = None
    if current_user.is_authenticated:
        user = current_user

    parlays = [DisplayableParlay(p, current_user) for p in Parlay.query.group_by(Parlay.Datetime).all()]
    #print(parlays)
    """ for parlay in parlays:
        for bet in parlay.bets:
            print(bet.success) """

    return render_template("parlays.html", user=user, dates=[parlays])


@app.route("/parlays/new", methods=["GET", "POST"])
def new_parlay():
    matchups = Matchup.query.filter(Matchup.Datetime > dt.datetime.now(dt.timezone.utc)).all()

    if request.method == "POST":
        user = current_user
        if not user:
            return redirect(url_for("login"))

        matchup_id = request.form.get("matchup")
        wager = request.form.get("wager")
        bet1_category = request.form.get("bet1_category")
        bet1_details = request.form.get("bet1_details")
        bet1_odds = request.form.get("bet1_odds")
        bet2_category = request.form.get("bet2_category")
        bet2_details = request.form.get("bet2_details")
        bet2_odds = request.form.get("bet2_odds")
        bet3_category = request.form.get("bet3_category")
        bet3_details = request.form.get("bet3_details")
        bet3_odds = request.form.get("bet3_odds")

        if not all([matchup_id, wager, bet1_category, bet1_details, bet1_odds, bet2_category, bet2_details, bet2_odds, bet3_category, bet3_details, bet3_odds]):
            return render_template("new.html", matchups=matchups, error="Please fill out all the fields")
        
        try:
            wager = float(wager)
            bet1_odds = float(bet1_odds)
            bet2_odds = float(bet2_odds)
            bet3_odds = float(bet3_odds)
            assert not (-100 < bet1_odds < 100 and -100 < bet2_odds < 100 and -100 < bet3_odds < 100), "Odds cannot be between -100 and +100."
        except (ValueError, AssertionError) as e:
            #print(f"{type(e)}{e}")
            return render_template("new.html", matchups=matchups, error="Wager and bet odds must be a numbers. Odds cannot be between -100 and 100.")
        
        if wager <= 0:
            return render_template("new.html", matchups=matchups, error="Wager must be greater than 0.")
        
        matchup = Matchup.query.filter_by(MatchupId = matchup_id).first()
        matchup_time = matchup.Datetime
        current_time = dt.datetime.now(dt.timezone.utc)
        print(f"Creating parlay: {user.Username}, {matchup.Away} @ {matchup.Home},", matchup_time, current_time)
        if matchup_time < current_time:
            return render_template("new.html", matchups=matchups, error="Matchup has already started.")
        
        bet1 = Bet(Category=sanitize(bet1_category), Details=sanitize(bet1_details), Odds=bet1_odds)
        bet2 = Bet(Category=sanitize(bet2_category), Details=sanitize(bet2_details), Odds=bet2_odds)
        bet3 = Bet(Category=sanitize(bet3_category), Details=sanitize(bet3_details), Odds=bet3_odds)

        db.session.add(bet1)
        db.session.add(bet2)
        db.session.add(bet3)
        db.session.commit()

        new_parlay = Parlay(Datetime=dt.datetime.now(), UserId=user.UserId, MatchupId=matchup_id, Wager=wager, BetId1=bet1.BetId, BetId2=bet2.BetId, BetId3=bet3.BetId)
        db.session.add(new_parlay)
        db.session.commit()
        return redirect(url_for("parlays"))
    else:
        return render_template("new.html", matchups=matchups)
    
@app.route("/parlays/edit/<int:parlay_id>", methods=["GET", "POST"])
def edit_parlay(parlay_id):
    matchups = Matchup.query.filter(Matchup.Datetime > dt.datetime.now(dt.timezone.utc)).all()

    try:
        parlay_id = int(parlay_id)
    except ValueError:
        return render_template("new.html", matchups=matchups, error="Invalid parlay id.")
    
    disParlay = DisplayableParlay(Parlay.query.filter_by(ParlayId=parlay_id).first())

    if request.method == "POST":
        user = current_user
        if not user:
            return redirect(url_for("login"))

        matchup_id = request.form.get("matchup")
        wager = request.form.get("wager")
        bet1_category = request.form.get("bet1_category")
        bet1_details = request.form.get("bet1_details")
        bet1_odds = request.form.get("bet1_odds")
        bet2_category = request.form.get("bet2_category")
        bet2_details = request.form.get("bet2_details")
        bet2_odds = request.form.get("bet2_odds")
        bet3_category = request.form.get("bet3_category")
        bet3_details = request.form.get("bet3_details")
        bet3_odds = request.form.get("bet3_odds")

        if not all([matchup_id, wager, bet1_category, bet1_details, bet1_odds, bet2_category, bet2_details, bet2_odds, bet3_category, bet3_details, bet3_odds]):
            return render_template("edit.html", matchups=matchups, parlay=disParlay, error="Please fill out all the fields")
        
        try:
            wager = float(wager)
            bet1_odds = float(bet1_odds)
            bet2_odds = float(bet2_odds)
            bet3_odds = float(bet3_odds)
            assert not (-100 < bet1_odds < 100 and -100 < bet2_odds < 100 and -100 < bet3_odds < 100), "Odds cannot be between -100 and +100."
        except (ValueError, AssertionError) as e:
            #print(f"{type(e)}{e}")
            return render_template("edit.html", matchups=matchups, parlay=disParlay, error="Wager and bet odds must be a numbers. Odds cannot be between -100 and 100.")
        
        if wager <= 0:
            return render_template("edit.html", matchups=matchups, parlay=disParlay, error="Wager must be greater than 0.")
        
        matchup = Matchup.query.filter_by(MatchupId = matchup_id).first()
        matchup_time = matchup.Datetime
        current_time = dt.datetime.now(dt.timezone.utc)
        print(f"Creating parlay: {user.Username}, {matchup.Away} @ {matchup.Home},", matchup_time, current_time)
        if matchup_time < current_time:
            return render_template("edit.html", matchups=matchups, parlay=disParlay, error="Matchup has already started.")
        
        bet1 = Bet(Category=sanitize(bet1_category), Details=sanitize(bet1_details), Odds=bet1_odds)
        bet2 = Bet(Category=sanitize(bet2_category), Details=sanitize(bet2_details), Odds=bet2_odds)
        bet3 = Bet(Category=sanitize(bet3_category), Details=sanitize(bet3_details), Odds=bet3_odds)

        db.session.add(bet1)
        db.session.add(bet2)
        db.session.add(bet3)
        db.session.commit()

        parlay = Parlay.query.filter_by(ParlayId=parlay_id).first()
        old_parlay = DisplayableParlay(parlay)
        parlay.MatchupId = matchup_id
        parlay.Wager = wager
        parlay.BetId1 = bet1.BetId
        parlay.BetId2 = bet2.BetId
        parlay.BetId3 = bet3.BetId
        db.session.commit()

        with open("edits.log", "a") as f:
            f.write(f"""
{dt.datetime.now().astimezone().strftime('%m/%d/%Y %I:%M %p')} - {user.Username} edited parlay {parlay_id}.
Matchup: {old_parlay.matchup.id} ({old_parlay.matchup.away} @ {old_parlay.matchup.home}) -> {matchup_id} ({matchup.Away} @ {matchup.Home})
Wager: {old_parlay.wager} -> {wager}
Bet 1: {old_parlay.bets[0].category}: {old_parlay.bets[0].details} ({old_parlay.bets[0].raw_odds}) -> {bet1_category}: {bet1_details} ({bet1_odds})
Bet 2: {old_parlay.bets[1].category}: {old_parlay.bets[1].details} ({old_parlay.bets[1].raw_odds}) -> {bet2_category}: {bet2_details} ({bet2_odds})
Bet 3: {old_parlay.bets[2].category}: {old_parlay.bets[2].details} ({old_parlay.bets[2].raw_odds}) -> {bet3_category}: {bet3_details} ({bet3_odds})
""")

        return redirect(url_for("parlays"))
    else:
        return render_template("edit.html", matchups=matchups, parlay=disParlay)
    
@app.route("/parlays/status", methods=["POST"])
@login_required
def update_parlay_status():
    data = request.get_json()
    bet_id = data.get("id")
    success = data.get("success")

    #print(f"Attemping to update bet {bet_id} to {success}")

    try:
        bet_id = int(bet_id)
    except ValueError:
        #print("Invalid bet id")
        return "Invalid bet id", 400
    
    success = None if success == "N" else success == "T"

    bet = Bet.query.filter_by(BetId=bet_id).first()
    if not bet:
        return "Bet not found", 404
    
    parlay = Parlay.query.filter((Parlay.BetId1 == bet_id) | (Parlay.BetId2 == bet_id) | (Parlay.BetId3 == bet_id)).first()
    if parlay.UserId != current_user.UserId:
        return "Unauthorized", 403
    
    #print(f"Updating bet {bet_id} to {success}")
    
    bet.Success = success
    db.session.commit()

    return "Success", 200

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
    