import datetime
import time
import re
month_dictionary = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12}


class Parser:

    _events = []

    @property
    def events(self):
        return self._events

    def __init__(self, path: str = ""):
        self.path: str = path

    def add_event(self, event: list[str], year: int):

        # ensure month and date

        dt = datetime.datetime.strptime(event[0][0:15], "%b%d %H%M%S.%f")
        date = datetime.datetime(year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)


        print(date)


    def clean_line(self, line: list) -> list:

        cleaned = line.copy()
        for element in line:
            if element == " " or element == "" or element == "\n":
                cleaned.remove(element)

        return cleaned

    def parse(self):
        file = open(self.path, "r")

        for i in range(4):
            file.readline()

        # extracting year from bulletin

        year = re.search(r"\b\d{4}\b", file.readline()).group()


        file.readline()
        file.readline()
        event = []

        for line in file:
            if line == "\n":
                self.add_event(event, year)
                break

                # event = []
                # continue

            event.append(line)

        print(event)


pars = Parser("2023_02_bul.txt")
pars.parse()
