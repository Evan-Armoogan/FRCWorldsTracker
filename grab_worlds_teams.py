import argparse
import typing
import statbotics
import google_sheets
from datetime import datetime
from zoneinfo import ZoneInfo
from api import get_event_match_data, get_event_rankings
from event_keys import *
from spreadsheet import *

type JSON = typing.Any

type Alliance = typing.Literal['Red', 'Blue']

TBA_LINK_PREFIX = 'https://www.thebluealliance.com'

class Match:
    __PLAYOFF_KEY_TO_NAME: dict[str, str] = {
        "sf1m1": "Upper Bracket - Round 1 - Match 1",
        "sf2m1": "Upper Bracket - Round 1 - Match 2",
        "sf3m1": "Upper Bracket - Round 1 - Match 3",
        "sf4m1": "Upper Bracket - Round 1 - Match 4",
        "sf5m1": "Lower Bracket - Round 2 - Match 5",
        "sf6m1": "Lower Bracket - Round 2 - Match 6",
        "sf7m1": "Upper Bracket - Round 2 - Match 7",
        "sf8m1": "Upper Bracket - Round 2 - Match 8",
        "sf9m1": "Lower Bracket - Round 3 - Match 9",
        "sf10m1": "Lower Bracket - Round 3 - Match 10",
        "sf11m1": "Upper Bracket - Round 4 - Match 11",
        "sf12m1": "Lower Bracket - Round 4 - Match 12",
        "sf13m1": "Lower Bracket - Round 5 - Match 13",
        "f1m1": "Finals 1",
        "f1m2": "Finals 2",
        "f1m3": "Finals Tiebreaker",
    }

    @classmethod
    def __key_to_match_name(cls, div: str, key: str) -> str:
        match_key = key.split("_")[1]
        if match_key[:2] == "qm":
            match_name =  f"Qualification {match_key[2:]}"
        else:
            match_name = cls.__PLAYOFF_KEY_TO_NAME.get(match_key)
        
        return f'{DIVISION_KEY_TO_NAME.get(div)} {match_name}'
    
    @staticmethod
    def __get_alliance_epa(teams: tuple[int, int, int], epas: dict[int, float]) -> float:
        epa: list[float] = [epas[team] for team in teams]
        return sum(epa)
    
    def __init__(self, division_key: str, match: JSON, epas: dict[int, float]) -> None:
        self.division_key = division_key

        self.completed = match['actual_time'] is not None
        
        self.key = match['key']
        self.name = Match.__key_to_match_name(self.division_key, self.key)

        red_teams = []
        for team in match['alliances']['red']['team_keys']:
            # The team names in response have 'frc' prepended (ex. 'frc4678')
            red_teams.append(int(team[len('frc'):]))
        self.red_teams = tuple(red_teams)
        self.red_score = match['alliances']['red']['score']
        self.red_epa = Match.__get_alliance_epa(self.red_teams, epas)

        blue_teams = []
        for team in match['alliances']['blue']['team_keys']:
            # The team names in response have 'frc' prepended (ex. 'frc4678')
            blue_teams.append(int(team[len('frc'):]))
        self.blue_teams = tuple(blue_teams)
        self.blue_score = match['alliances']['blue']['score']
        self.blue_epa = Match.__get_alliance_epa(self.blue_teams, epas)

        self.breakdown_link = f'{TBA_LINK_PREFIX}/match/{self.key}'
        self.time_estimate = match['predicted_time'] if match['predicted_time'] is not None else match['time']
        self.time_completed = match['actual_time']

        self.winner = None if match['winning_alliance'] == '' else match['winning_alliance'].capitalize()

        self.stream_link = STREAM_LINKS.get(self.division_key)
    
    division_key: str
    completed: bool
    key: str
    name: str
    red_teams: tuple[int, int, int]
    blue_teams: tuple[int, int, int]
    red_score: int
    blue_score: int
    red_epa: int
    blue_epa: int
    breakdown_link: str
    time_estimate: int
    time_completed: int
    winner: Alliance | None
    stream_link: str


class TeamRankings:
    def __init__(self, team: JSON):
        self.rank = team['rank']
        self.team = int(team['team_key'][len('frc'):])

        STAT_INDEX = {
            'ranking_score': 0,
            'avg_coop': 1,
            'avg_match': 2,
            'avg_auto': 3,
            'avg_endgame': 4,
        }
        stats = team['sort_orders']
        self.ranking_score = stats[STAT_INDEX['ranking_score']]
        self.avg_coop = stats[STAT_INDEX['avg_coop']]
        self.avg_match = stats[STAT_INDEX['avg_match']]
        self.avg_auto = stats[STAT_INDEX['avg_auto']]
        self.avg_endgame = stats[STAT_INDEX['avg_endgame']]

        record = team['record']
        self.wins = record['wins']
        self.losses = record['losses']
        self.ties = record['ties']

        self.dq = team['dq']
        self.played = team['matches_played']

        self.total_rp = team['extra_stats'][0]

    rank: int
    team: int
    ranking_score: float
    avg_coop: float
    avg_match: float
    avg_auto: float
    avg_endgame: float
    wins: int
    losses: int
    ties: int
    dq: int
    played: int
    total_rp: int


class DataFilter:
    def __init__(self, teams_of_interest: tuple[int, ...]) -> None:
        self.teams_of_interest = teams_of_interest

    def match_filter(self, match: Match) -> bool:
        teams_in_match = match.red_teams + match.blue_teams

        # Creates a set for teams in match and teams we care about. If there is an intersection,
        # at least one team that we care about is playing in the match.
        return len(set(teams_in_match).intersection(set(self.teams_of_interest))) > 0

    def team_filter(self, team: TeamRankings) -> bool:
        return team.team in self.teams_of_interest
    
    teams_of_interest: tuple[int, ...]


# NOTE: This function takes several seconds to run
def get_team_epas() -> dict[int, float]:
    sb = statbotics.Statbotics()
    LIMIT = 1000
    offset = 0
    data: list[JSON] = []
    while True:
        try:
            data += sb.get_team_years(year=YEAR, limit=LIMIT, offset=offset)
        except UserWarning:
            # UserWarning is raised when the query returns no teams (i.e. we've retrieved all active teams)
            break
        offset += LIMIT
    
    epas: dict[int, float] = {
        team['team']: team['epa']['total_points']['mean']
        for team in data
    }
    return epas


def get_list_of_matches(event_key: str, epas: dict[int, float]) -> list[Match]:
    # Grab all teams at event from TBA. Get all these teams EPA from statbotics
    response = get_event_match_data(event_key)
    matches: list[Match] = []
    for match in response:
        matches.append(Match(event_key, match, epas))
    return matches


def get_recent_and_upcoming_matches(teams_of_interest: tuple[int, ...]) -> tuple[list[Match], list[Match]]:
    epas = get_team_epas()
    matches: dict[str, list[Match]] = {
        key: get_list_of_matches(key, epas)
        for key in DIVISION_KEYS
    }

    # Remove all matches without teams we are interested in
    data_filter = DataFilter(teams_of_interest)
    for division in DIVISION_KEYS:
        matches[division] = list(filter(data_filter.match_filter, matches[division]))

    # Aggregate all matches into completed and not completed
    completed: list[Match] = []
    not_completed: list[Match] = []
    for division in DIVISION_KEYS:
        completed += [match for match in matches[division] if match.completed]
        not_completed += [match for match in matches[division] if not match.completed]

    completed.sort(reverse=True, key=lambda x: x.time_completed)
    not_completed.sort(reverse=False, key=lambda x: x.time_estimate)

    return completed, not_completed


def write_past_matches(
    spreadsheet: google_sheets.GoogleSheets,
    matches: list[Match],
    teams_of_interest: tuple[int, ...]
) -> google_sheets.GoogleSheets:
    header = google_sheets.Row([
        google_sheets.Cell('Match', alignment='Center'),
        google_sheets.Cell('Red Alliance', cell_colour='Red', length=3, alignment='Center'),
        google_sheets.Cell('Red Score', cell_colour='Red', alignment='Center'),
        google_sheets.Cell('Blue Score', cell_colour='Blue', alignment='Center'),
        google_sheets.Cell('Blue Alliance', cell_colour='Blue', length=3, alignment='Center'),
        google_sheets.Cell('TBA Breakdown', alignment='Center')
    ])

    sheet = google_sheets.Sheet(PAST_MATCHES_SHEET_ID, header)
    
    for match in matches:
        sheet.append_row([
            google_sheets.Cell(match.name),
            google_sheets.Cell(str(match.red_teams[0]), cell_colour='Red', bold=match.red_teams[0] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_teams[1]), cell_colour='Red', bold=match.red_teams[1] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_teams[2]), cell_colour='Red', bold=match.red_teams[2] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_score), cell_colour='Red', bold=match.winner == 'Red'),
            google_sheets.Cell(str(match.blue_score), cell_colour='Blue', bold=match.winner == 'Blue'),
            google_sheets.Cell(str(match.blue_teams[0]), cell_colour='Blue', bold=match.blue_teams[0] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.blue_teams[1]), cell_colour='Blue', bold=match.blue_teams[1] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.blue_teams[2]), cell_colour='Blue', bold=match.blue_teams[2] in teams_of_interest, italic=True),
            google_sheets.Cell(match.breakdown_link)
        ])

    spreadsheet.add_sheet(sheet)
    return spreadsheet


def write_upcoming_matches(
    spreadsheet: google_sheets.GoogleSheets,
    matches: list[Match],
    teams_of_interest: tuple[int, ...]
) -> google_sheets.GoogleSheets:
    header = google_sheets.Row([
        google_sheets.Cell('Match', alignment='Center'),
        google_sheets.Cell('Red Alliance', cell_colour='Red', length=3, alignment='Center'),
        google_sheets.Cell('Red EPA', cell_colour='Red', alignment='Center'),
        google_sheets.Cell('Blue EPA', cell_colour='Blue', alignment='Center'),
        google_sheets.Cell('Blue Alliance', cell_colour='Blue', length=3, alignment='Center'),
        google_sheets.Cell('Time (ET)', alignment='Center'),
        google_sheets.Cell('Stream', alignment='Center')
    ])

    sheet = google_sheets.Sheet(UPCOMING_MATCHES_SHEET_ID, header)
    
    for match in matches:
        sheet.append_row([
            google_sheets.Cell(match.name),
            google_sheets.Cell(str(match.red_teams[0]), cell_colour='Red', bold=match.red_teams[0] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_teams[1]), cell_colour='Red', bold=match.red_teams[1] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_teams[2]), cell_colour='Red', bold=match.red_teams[2] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.red_epa), cell_colour='Red', bold=match.red_epa > match.blue_epa),
            google_sheets.Cell(str(match.blue_epa), cell_colour='Blue', bold=match.blue_epa > match.red_epa),
            google_sheets.Cell(str(match.blue_teams[0]), cell_colour='Blue', bold=match.blue_teams[0] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.blue_teams[1]), cell_colour='Blue', bold=match.blue_teams[1] in teams_of_interest, italic=True),
            google_sheets.Cell(str(match.blue_teams[2]), cell_colour='Blue', bold=match.blue_teams[2] in teams_of_interest, italic=True),
            google_sheets.Cell(
                datetime.fromtimestamp(match.time_estimate).astimezone().astimezone(ZoneInfo('America/New_York')).isoformat(),
                datetime='ddd h:mm AM/PM'
            ),
            google_sheets.Cell(match.stream_link)
        ])

    spreadsheet.add_sheet(sheet)
    return spreadsheet


def get_rankings(event_key: str, teams_of_interest: tuple[int, ...]) -> list[TeamRankings]:
    data = get_event_rankings(event_key)
    rankings = [TeamRankings(team_ranking) for team_ranking in data['rankings']]
    data_filter = DataFilter(teams_of_interest)
    filtered_rankings: list[TeamRankings] = list(filter(data_filter.team_filter, rankings))
    filtered_rankings.sort(reverse=False, key=lambda x: x.rank)
    return filtered_rankings


def write_rankings(
    spreadsheet: google_sheets.GoogleSheets,
    teams_of_interest: tuple[int, ...]
) -> google_sheets.GoogleSheets:
    for division in DIVISION_KEYS:
        if DIVISION_RANKINGS_SHEET_IDS.get(division) is None:
            continue  # Einstein doesn't have qualifications rankings

        header = google_sheets.Row([
            google_sheets.Cell('Rank', alignment='Center'),
            google_sheets.Cell('Team', alignment='Center'),
            google_sheets.Cell('Ranking Score', alignment='Center'),
            google_sheets.Cell('Avg Coop', alignment='Center'),
            google_sheets.Cell('Avg Match', alignment='Center'),
            google_sheets.Cell('Avg Auto', alignment='Center'),
            google_sheets.Cell('Avg Endgame', alignment='Center'),
            google_sheets.Cell('Record (W-L-T)', alignment='Center'),
            google_sheets.Cell('DQ', alignment='Center'),
            google_sheets.Cell('Played', alignment='Center'),
            google_sheets.Cell('Total Ranking Points', alignment='Center')
        ])

        sheet = google_sheets.Sheet(DIVISION_RANKINGS_SHEET_IDS.get(division), header)

        rankings = get_rankings(division, teams_of_interest)
        for team in rankings:
            sheet.append_row([
                google_sheets.Cell(str(team.rank)),
                google_sheets.Cell(str(team.team)),
                google_sheets.Cell(str(team.ranking_score)),
                google_sheets.Cell(str(team.avg_coop)),
                google_sheets.Cell(str(team.avg_match)),
                google_sheets.Cell(str(team.avg_auto)),
                google_sheets.Cell(str(team.avg_endgame)),
                # apostrophe prefix prevents sheets from interpreting this as datetime
                google_sheets.Cell(f"'{team.wins}-{team.losses}-{team.ties}"),
                google_sheets.Cell(str(team.dq)),
                google_sheets.Cell(str(team.played)),
                google_sheets.Cell(str(team.total_rp))
            ])
        
        sheet.append_row([])  # Empty row

        sheet.append_row([
            google_sheets.Cell(f'=HYPERLINK("{TBA_LINK_PREFIX}/event/{division}#rankings", "Full Rankings")')
        ])

        spreadsheet.add_sheet(sheet)
    
    return spreadsheet


def write_matches(teams_of_interest: tuple[int, ...]) -> None:
    spreadsheet = google_sheets.GoogleSheets(SPREADSHEET_ID)
    past, upcoming = get_recent_and_upcoming_matches(teams_of_interest)
    spreadsheet = write_past_matches(spreadsheet, past, teams_of_interest)
    spreadsheet = write_upcoming_matches(spreadsheet, upcoming, teams_of_interest)
    spreadsheet = write_rankings(spreadsheet, teams_of_interest)
    spreadsheet.write()


def main(teams_of_interest: tuple[int, ...]) -> None:
    write_matches(teams_of_interest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--teams', help='Enter teams to output', type=int, nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        main(parse_args().teams)
    except KeyboardInterrupt:
        pass
