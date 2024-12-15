from app import app, db, Matchup
import datetime as dt
import pytz

matchups = [
    {"Home": "New Jersey Devils", "Away": "Chicago Blackhawks", "Datestr": "2024-12-14 11:00 am"},
    {"Home": "New York Rangers", "Away": "Los Angeles Kings", "Datestr": "2024-12-14 11:00 am"},
    {"Home": "Minnesota Wild", "Away": "Philadelphia Flyers", "Datestr": "2024-12-14 12:00 pm"},
    {"Home": "Edmonton Oilers", "Away": "Vegas Golden Knights", "Datestr": "2024-12-14 2:00 pm"},
    {"Home": "Ottawa Senators", "Away": "Pittsburgh Penguins", "Datestr": "2024-12-14 5:00 pm"},
    {"Home": "Detroit Red Wings", "Away": "Toronto Maple Leafs", "Datestr": "2024-12-14 5:00 pm"},
    {"Home": "Washington Capitals", "Away": "Buffalo Sabres", "Datestr": "2024-12-14 5:00 pm"},
    {"Home": "Columbus Blue Jackets", "Away": "Anaheim Ducks", "Datestr": "2024-12-14 5:00 pm"},
    {"Home": "Winnipeg Jets", "Away": "Montreal Canadiens", "Datestr": "2024-12-14 5:00 pm"},
    {"Home": "Dallas Stars", "Away": "St. Louis Blues", "Datestr": "2024-12-14 6:00 pm"},
    {"Home": "Colorado Avalanche", "Away": "Nashville Predators", "Datestr": "2024-12-14 7:00 pm"},
    {"Home": "Calgary Flames", "Away": "Florida Panthers", "Datestr": "2024-12-14 8:00 pm"},
    {"Home": "Vancouver Canucks", "Away": "Boston Bruins", "Datestr": "2024-12-14 8:00 pm"},
    {"Home": "San Jose Sharks", "Away": "Utah Hockey Club", "Datestr": "2024-12-14 8:00 pm"},
    {"Home": "Seattle Kraken", "Away": "Tampa Bay Lightning", "Datestr": "2024-12-14 8:00 pm"},
    {"Home": "Chicago Blackhawks", "Away": "New York Islanders", "Datestr": "2024-12-15 1:00 pm"},
    {"Home": "Toronto Maple Leafs", "Away": "Buffalo Sabres", "Datestr": "2024-12-15 3:00 pm"},
    {"Home": "Carolina Hurricanes", "Away": "Columbus Blue Jackets", "Datestr": "2024-12-15 3:00 pm"},
    {"Home": "New York Rangers", "Away": "St. Louis Blues", "Datestr": "2024-12-15 4:00 pm"},
    {"Home": "Minnesota Wild", "Away": "Vegas Golden Knights", "Datestr": "2024-12-15 4:00 pm"}
]

with app.app_context():
        if input("Would you like to clear existing matchups? (y/N): ") == "y":
            db.session.query(Matchup).delete()
            db.session.commit()

        mst = pytz.timezone("US/Mountain")

        for matchup in matchups:
            datetime = mst.localize(dt.datetime.strptime(matchup["Datestr"], "%Y-%m-%d %I:%M %p"))
            new_matchup = Matchup(Datetime=datetime.astimezone(dt.timezone.utc), Home=matchup["Home"], Away=matchup["Away"])
            db.session.add(new_matchup)
            db.session.commit()