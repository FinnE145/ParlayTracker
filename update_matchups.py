from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Away": "Philadelphia Flyers", "Home": "Detroit Redwings", "Datestr": "2024-12-17 5:00 pm"},
    {"Away": "Toronto Maple Leafs", "Home": "Dallas Stars", "Datestr": "2024-12-17 5:30 pm"},
    {"Away": "Florida Panthers", "Home": "Minnesota Wild", "Datestr": "2024-12-17 7:30 pm"},
    {"Away": "Vancouver Canucks", "Home": "Utah Hockey Club", "Datestr": "2024-12-17 8:00 pm"},
    {"Away": "Winnipeg Jets", "Home": "Anaheim Ducks", "Datestr": "2024-12-17 8:00 pm"}
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