from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Home": "Dallas Stars", "Away": "Washington Capitals", "Datestr": "2024-12-16 6:00 pm"},
    {"Home": "Edmonton Oilers", "Away": "Florida Panthers", "Datestr": "2024-12-16 6:30 pm"},
    {"Home": "Vancouver Canucks", "Away": "Colorado Avalanche", "Datestr": "2024-12-16 8:30 pm"}
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