from nhlpy import NHLClient
from iformat import iprint
import datetime as dt

client = NHLClient()

def get_matchups(date:dt.date):
    date = date.strftime("%Y-%m-%d")
    matchups_data = client.schedule.get_schedule(date)
    return [{
        "datetime": dt.datetime.strptime(m["startTimeUTC"], "%Y-%m-%dT%H:%M:%SZ"),
        "awayTeam": f"{m['awayTeam']['placeName']['default']} {m['awayTeam']['commonName']['default']}",
        "homeTeam": f"{m['homeTeam']['placeName']['default']} {m['homeTeam']['commonName']['default']}"
    } for m in matchups_data['games']]

def get_matchup_count(date:dt.date):
    date = date.strftime("%Y-%m-%d")
    return int(client.schedule.get_schedule(date)["numberOfGames"])