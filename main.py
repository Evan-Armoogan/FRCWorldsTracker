import argparse
import time
from grab_worlds_teams import main as grab_write_data

UPDATE_PERIOD = 5*60  # 5 minutes


def main(teams: tuple[int, ...]) -> None:
    while True:
        grab_write_data(teams)
        time.sleep(UPDATE_PERIOD)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--teams', help='Enter teams to output', type=int, nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        main(parse_args().teams)
    except KeyboardInterrupt:
        pass
