from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Home": "Chicago Blackhawks", "Away": "New York Islanders", "Datestr": "1:00 pm"},
    {"Home": "Toronto Maple Leafs", "Away": "Buffalo Sabres", "Datestr": "3:00 pm"},
    {"Home": "Carolina Hurricanes", "Away": "Columbus Blue Jackets", "Datestr": "3:00 pm"},
    {"Home": "New York Rangers", "Away": "St. Louis Blues", "Datestr": "4:00 pm"},
    {"Home": "Minnesota Wild", "Away": "Vegas Golden Knights", "Datestr": "4:00 pm"}
]

with app.app_context():
        db.session.query(Matchup).delete()
        db.session.commit()

        mst = pytz.timezone("US/Mountain")

        for matchup in matchups:
            datetime = mst.localize(dt.datetime.strptime("2024-12-14 " + matchup["Datestr"], "%Y-%m-%d %I:%M %p"))
            new_matchup = Matchup(Datetime=datetime.astimezone(dt.timezone.utc), Home=matchup["Home"], Away=matchup["Away"])
            db.session.add(new_matchup)
            db.session.commit()