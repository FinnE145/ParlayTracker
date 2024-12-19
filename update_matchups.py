from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Away": "St. Louis Blues", "Home": "Tampa Bay Lightning", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "New Jersey Devils", "Home": "Columbus Blue Jackets", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "Los Angeles Kings", "Home": "Philadelphia Flyers", "Datestr": "2024-12-19 5:30 pm"},
    {"Away": "Pitsburg Penguins", "Home": "Nashville Predators", "Datestr": "2024-12-19 6:00 pm"},
    {"Away": "Seattle Kraken", "Home": "Chicago Blackhawks", "Datestr": "2024-12-19 6:30 pm"},
    {"Away": "Ottawa Sentators", "Home": "Calgary Flames", "Datestr": "2024-12-19 7:00 pm"},
    {"Away": "Boston Bruins", "Home": "Edmonton Oilers", "Datestr": "2024-12-19 7:00 pm"},
    {"Away": "Vancouver Canucks", "Home": "Vegas GOlden Knights", "Datestr": "2024-12-19 8:00 pm"},
    {"Away": "Colorado Avalanche", "Home": "San Jose Sharks", "Datestr": "2024-12-19 8:30 pm"}
]

with app.app_context():
        if input("Would you like to clear existing matchups? (y/N): ").lower() in ["y", "yes"]:
            db.session.query(Matchup).delete()
            db.session.commit()

        mst = pytz.timezone("US/Mountain")

        for matchup in matchups:
            datetime = mst.localize(dt.datetime.strptime(matchup["Datestr"], "%Y-%m-%d %I:%M %p"))
            new_matchup = Matchup(Datetime=datetime.astimezone(dt.timezone.utc), Home=matchup["Home"], Away=matchup["Away"])
            db.session.add(new_matchup)
            db.session.commit()