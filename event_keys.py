from config import CONFIG

YEAR: int = CONFIG.year

ARCHIMEDES_KEY: str = f'{YEAR}arc'
CURIE_KEY: str = f'{YEAR}cur'
DALY_KEY: str = f'{YEAR}dal'
GALILEO_KEY: str = f'{YEAR}gal'
HOPPER_KEY: str = f'{YEAR}hop'
JOHNSON_KEY: str = f'{YEAR}joh'
MILSTEIN_KEY: str = f'{YEAR}mil'
NEWTON_KEY: str = f'{YEAR}new'
EINSTEIN_KEY: str = f'{YEAR}cmptx'

DIVISION_KEYS: list[str] = [
    ARCHIMEDES_KEY,
    CURIE_KEY,
    DALY_KEY,
    GALILEO_KEY,
    HOPPER_KEY,
    JOHNSON_KEY,
    MILSTEIN_KEY,
    NEWTON_KEY,
    EINSTEIN_KEY
]

DIVISION_KEY_TO_NAME: dict[str, str] = {
    ARCHIMEDES_KEY: 'Archimedes',
    CURIE_KEY: 'Curie',
    DALY_KEY: 'Daly',
    GALILEO_KEY: 'Galileo',
    HOPPER_KEY: 'Hopper',
    JOHNSON_KEY: 'Johnson',
    MILSTEIN_KEY: 'Milstein',
    NEWTON_KEY: 'Newton',
    EINSTEIN_KEY: 'Einstein'
}

STREAM_LINKS: dict[str, str] = {
    ARCHIMEDES_KEY: 'https://www.twitch.tv/firstinspires_archimedes',
    CURIE_KEY: 'https://www.twitch.tv/firstinspires_curie',
    DALY_KEY: 'https://www.twitch.tv/firstinspires_daly',
    GALILEO_KEY: 'https://www.twitch.tv/firstinspires_galileo',
    HOPPER_KEY: 'https://www.twitch.tv/firstinspires_hopper',
    JOHNSON_KEY: 'https://www.twitch.tv/firstinspires_johnson',
    MILSTEIN_KEY: 'https://www.twitch.tv/firstinspires_milstein',
    NEWTON_KEY: 'https://www.twitch.tv/firstinspires_newton',
    EINSTEIN_KEY: 'https://www.twitch.tv/firstinspires',
}
