import datetime
import pandas
import re


class Parser:

    _records = []

    @property
    def records(self):
        return self._records

    def __init__(self, path: str = ""):
        self.path: str = path

    def addRecord(self, record: list[str], year: int):

        if len(record) == 0:
            return

        # extracting date
        date = None

        date_string = re.search(r"[A-Z]+[0-9]+", record[0])

        if date_string:
            datetimeVar = datetime.datetime.strptime(date_string.group(), "%b%d")
            date = datetime.datetime(year, datetimeVar.month, datetimeVar.day)

        # extracting date and time, if event has time

        date_string = re.search(r"[A-Z]+[0-9]+\s+\d+\.\d+", record[0])

        if date_string:
            datetimeVar = datetime.datetime.strptime(date_string.group(), "%b%d %H%M%S.%f")
            date = datetime.datetime(year,
                                     datetimeVar.month,
                                     datetimeVar.day,
                                     datetimeVar.hour,
                                     datetimeVar.minute,
                                     datetimeVar.second,
                                     datetimeVar.microsecond)

        # extracting country

        country = None
        test = re.search(r"\.\d+\s+(.+)\(\d+\)", record[0])
        if test:
            country = re.sub(r"[.\d\(\)]", "", test.group()).strip()

        # extracting latitude and longitude

        lat = None
        lon = None

        if re.search(r"\d+.\d+N", record[0]):
            lat = float(re.search(r"\d+.\d+N", record[0]).group().replace("N", ""))

        if re.search(r"\d+.\d+E", record[0]):
            lon = float(re.search(r"\d+.\d+E", record[0]).group().replace("E", ""))

        # extracting locationID
        locationID = None
        locationMatch = re.search(r"\((\d+)\)", record[0])

        if locationMatch:
            locationID = int(re.sub(r"[()]", "", locationMatch.group()))

        # creating DataFrame with information about stations

        # checking if line is in correct format and adding it to queue
        stationInfoQueue = []
        for line in record:

            lineMatch = re.search(r"[A-Z]+\s+e(Pg)|(Sg)+\s+\d+\.\d+", line.strip())
            if lineMatch:
                stationInfoQueue.append(line.strip())

        # creating table
        stationNameList = []
        stationPgList = []
        stationSgList = []
        for station in stationInfoQueue:

            # extracting station name

            stationName = None
            stationNameMatch = re.search(r"^[A-Z]+", station)
            if stationNameMatch:
                stationName = stationNameMatch.group()
                stationNameList.append(stationName)

            # extracting Pg
            stationPgTimeMatch = re.search(r"ePg\s+\d+\.\d+", station)

            if stationPgTimeMatch:
                timeText = re.sub(r"[ePg]", "", stationPgTimeMatch.group()).strip()
                stationPgTimeVar = datetime.datetime.strptime(timeText, "%H%M%S.%f")

                stationPgTime = datetime.datetime(year,
                                                  date.month,
                                                  date.day,
                                                  stationPgTimeVar.hour,
                                                  stationPgTimeVar.minute,
                                                  stationPgTimeVar.second,
                                                  stationPgTimeVar.microsecond)
                stationPgList.append(stationPgTime)
            else:
                stationPgList.append(None)

            # extracting Sg
            stationSgTimeMatch = re.search(r"eSg\s+\d+\.\d+", station)

            if stationSgTimeMatch:
                timeText = re.sub(r"[eSg]", "", stationSgTimeMatch.group()).strip()
                stationSgTimeVar = datetime.datetime.strptime(timeText, "%H%M%S.%f")

                stationSgTime = datetime.datetime(year,
                                                  date.month,
                                                  date.day,
                                                  stationSgTimeVar.hour,
                                                  stationSgTimeVar.minute,
                                                  stationSgTimeVar.second,
                                                  stationSgTimeVar.microsecond)
                stationSgList.append(stationSgTime)
            else:
                stationSgList.append(None)

        # creating dictionary and DataFrame and adding record to a record list

        arrivalTimes = {
            "station": stationNameList,
            "pg_arrival_time": stationPgList,
            "sg_arrival_time": stationSgList
        }
        stationDataFrame = pandas.DataFrame(arrivalTimes)

        recordDictionary = {"time": date,
                            "lat": lat,
                            "lon": lon,
                            "country": country,
                            "location_id": locationID,
                            "arrival_times": stationDataFrame}

        self._records.append(recordDictionary)

    def parse(self):
        file = open(self.path, "r")

        for i in range(4):
            file.readline()

        # extracting year of a file
        year = int(re.search(r"\b\d{4}\b", file.readline()).group())

        file.readline()
        file.readline()
        record = []

        for line in file:
            if line == "Copyright (c) Institute of Geophysics CAS Prague\n":
                break
            if line == "\n":
                self.addRecord(record, year)
                record = []
                continue

            record.append(line)


pars = Parser("2023_02_bul.txt")
pars.parse()
for rec in pars.records:
    print(rec)
