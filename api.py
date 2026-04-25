import requests
import json
import typing

type JSON = typing.Any

BASE_URL = "https://www.thebluealliance.com/api/v3"

def do_api_call(url: str) -> JSON:
    f = open(".tba_api_key", "r")
    r = requests.get(url=url, headers={"X-TBA-Auth-Key": f.read().strip()})
    return r.json()


def get_event_match_data(event_key: str) -> JSON:
    url = f"{BASE_URL}/event/{event_key}/matches/simple"
    return do_api_call(url)

def get_team_match_data(team: int, year: int) -> JSON:
    url = f"{BASE_URL}/team/frc{team}/matches/{year}/simple"
    return do_api_call(url)

def get_event_rankings(event_key: str) -> JSON:
    url = f"{BASE_URL}/event/{event_key}/rankings"
    return do_api_call(url)


def main() -> None:
    # for testing
    with open("output.json", "w") as f:
        json.dump(get_event_match_data('2025cur'), f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
