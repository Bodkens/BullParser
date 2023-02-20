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

    _records = []

    @property
    def records(self):
        return self._records

    def __init__(self, path: str = ""):
        self.path: str = path

    def add_record(self, record: list[str], year: int):

        if len(record) == 0:
            return
        datetime_var = None
        date = None

        date_string = re.search(r"[A-Z]+[0-9]+\s+\d+\.\d+", record[0])

        if date_string:
            datetime_var = datetime.datetime.strptime(date_string.group(), "%b%d %H%M%S.%f")
            date = datetime.datetime(year,
                                     datetime_var.month,
                                     datetime_var.day,
                                     datetime_var.hour,
                                     datetime_var.minute,
                                     datetime_var.second,
                                     datetime_var.microsecond)

        country = None
        test = re.search(r"\.\d+\s+(.+)\(\d+\)", record[0])
        if test:
            country = re.sub("[.\d\(\)]", "", test.group()).strip()

        lat = None
        lot = None

        if re.search(r"\d+.\d+N", record[0]):
            lat = float(re.search(r"\d+.\d+N", record[0]).group().replace("N", ""))

        if re.search(r"\d+.\d+E", record[0]):
            lot = float(re.search(r"\d+.\d+E", record[0]).group().replace("E", ""))

        location_id = None

        if re.search(r"\((\d+)\)", record[0]):
            location_id = int(re.search(r"\((\d+)\)", record[0]).group().replace("(", "").replace(")", ""))

        record_dictionary = {"time": date, "lat": lat, "lot": lot, "country": country, "location_id": location_id}

        self._records.append(record_dictionary)
        print(record_dictionary)

    def parse(self):
        file = open(self.path, "r")

        for i in range(4):
            file.readline()

        year = int(re.search(r"\b\d{4}\b", file.readline()).group())

        file.readline()
        file.readline()
        record = []

        for line in file:
            if line == "Copyright (c) Institute of Geophysics CAS Prague":
                break
            if line == "\n":
                self.add_record(record, year)
                record = []
                continue

            record.append(line)

        print(record)


pars = Parser("2023_02_bul.txt")
pars.parse()
for rec in pars.records:
    print(rec)
