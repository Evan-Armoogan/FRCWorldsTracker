import google_sheets
from datetime import datetime

def sheet_test() -> None:
    header = google_sheets.Row([
        google_sheets.Cell('Match'),
        google_sheets.Cell('Red', cell_colour='Red', length=3, alignment='Center'),
        google_sheets.Cell('Red Score', cell_colour='Red'),
        google_sheets.Cell('Blue Score', cell_colour='Blue'),
        google_sheets.Cell('Blue', cell_colour='Blue', length=3, alignment='Center'),
        google_sheets.Cell('TBA Breakdown'),
        google_sheets.Cell('Time (ET)')
    ])

    sheet = google_sheets.Sheet(72756875, header)
    sheet.append_row([
            google_sheets.Cell('Newton Qualification 1'),
            google_sheets.Cell('2056', cell_colour='Red', bold=True, italic=True),
            google_sheets.Cell('4678', cell_colour='Red', italic=True),
            google_sheets.Cell('1678', cell_colour='Red', italic=True),
            google_sheets.Cell('300', cell_colour='Red', bold=True),
            google_sheets.Cell('251', cell_colour='Blue'),
            google_sheets.Cell('118', cell_colour='Blue', italic=True),
            google_sheets.Cell('1114', cell_colour='Blue', bold=True, italic=True),
            google_sheets.Cell('254', cell_colour='Blue', italic=True),
            google_sheets.Cell('https://www.thebluealliance.com/match/2025oncmp_f1m1'),
            google_sheets.Cell(datetime.fromtimestamp(1744068219).isoformat(), datetime='ddd h:mm AM/PM')
    ])

    SPREADSHEET_ID = '1V6LoRB9yLSjy9yhGqRE22ge9v2v3FHlIk6pwzfX_1-Q'
    spreadsheet = google_sheets.GoogleSheets(SPREADSHEET_ID)
    spreadsheet.add_sheet(sheet)
    spreadsheet.write()

if __name__ == "__main__":
    sheet_test()
