from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Away": "Toronto Maple Leafs", "Home": "Buffalo Sabres", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "Montreal Canadiens", "Home": "Detroit Redwings", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "St. Louis Blues", "Home": "Florida Panthers", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "Carolina Hurricanes", "Home": "Washington Capitals", "Datestr": "2024-12-19 5:00 pm"},
    {"Away": "New York Rangers", "Home": "Dallas Stars", "Datestr": "2024-12-19 6:30 pm"},
    {"Away": "Utah Hockey Club", "Home": "Minnesota Wild", "Datestr": "2024-12-19 6:00 pm"},
    {"Away": "Colorado Avalanche", "Home": "Anaheim Ducks", "Datestr": "2024-12-19 8:00 pm"}
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