from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Home": "Montreal Canadiens", "Away": "Buffalo Sabres", "Datestr": "2024-12-17 5:00 pm"},
    {"Home": "Tampa Bay Lightning", "Away": "Colombus Blue Jackets", "Datestr": "2024-12-17 5:00 pm"},
    {"Home": "Pitsburg Penguins", "Away": "Los Angeles Kings", "Datestr": "2024-12-17 5:00 pm"},
    {"Home": "Carolina Hurricanes", "Away": "New York Islanders", "Datestr": "2024-12-17 5:30 pm"},
    {"Home": "St. Louis Blues", "Away": "New Jersey Devils", "Datestr": "2024-12-17 6:00 pm"},
    {"Home": "Nashville Predators", "Away": "New York Rangers", "Datestr": "2024-12-17 6:00 pm"},
    {"Home": "Chicago Blackhawks", "Away": "Washington Capitals", "Datestr": "2024-12-17 6:30 pm"},
    {"Away": "Boston Bruins", "Home": "Calgary Flames", "Datestr": "2024-12-17 7:00 pm"},
    {"Away": "Ottawa Senators", "Home": "Seattle Kraken", "Datestr": "2024-12-17 8:00 pm"},
    {"Home": "San Jose Sharks", "Away": "Winnipeg Jets", "Datestr": "2024-12-17 8:30 pm"}
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