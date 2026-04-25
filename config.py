import json

class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            self.spreadsheet_id = config_data['spreadsheet_id']
            self.past_matches_sheet_id = config_data['past_matches_sheet_id']
            self.upcoming_matches_sheet_id = config_data['upcoming_matches_sheet_id']
            self.archimedes_rankings_sheet_id = config_data['archimedes_rankings_sheet_id']
            self.curie_rankings_sheet_id = config_data['curie_rankings_sheet_id']
            self.daly_rankings_sheet_id = config_data['daly_rankings_sheet_id']
            self.galileo_rankings_sheet_id = config_data['galileo_rankings_sheet_id']
            self.hopper_rankings_sheet_id = config_data['hopper_rankings_sheet_id']
            self.johnson_rankings_sheet_id = config_data['johnson_rankings_sheet_id']
            self.milstein_rankings_sheet_id = config_data['milstein_rankings_sheet_id']
            self.newton_rankings_sheet_id = config_data['newton_rankings_sheet_id']
            self.year = config_data['year']

    spreadsheet_id: str
    past_matches_sheet_id: int
    upcoming_matches_sheet_id: int
    archimedes_rankings_sheet_id: int
    curie_rankings_sheet_id: int
    daly_rankings_sheet_id: int
    galileo_rankings_sheet_id: int
    hopper_rankings_sheet_id: int
    johnson_rankings_sheet_id: int
    milstein_rankings_sheet_id: int
    newton_rankings_sheet_id: int
    year: int

CONFIG = Config()
