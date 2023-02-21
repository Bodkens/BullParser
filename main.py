import datetime
import pandas
import re


class Parser:

    _records = []

    @property
    def records(self):
        return self._records

    def __init__(self, path: str = ''):
        self.path: str = path

    def addRecord(self, record: list[str], year: int):

        if len(record) == 0:
            return

        # checking if record having suitable station info and adding it, if record does not have any, we will not add it
        station_info_queue = []
        station_name_list = []
        station_pg_list = []
        station_sg_list = []
        correct_station_lines_present = False
        for line in record:

            line_match = re.search(r'[A-Z]+\s+e(Pg)|(Sg)+\s+\d+\.\d+', line.strip())
            if line_match:
                correct_station_lines_present = True
                station = line.strip()
                date = None

                # extracting month and day from first line
                date_string = re.search(r'[A-Z]+[0-9]+', record[0])
                station_info_queue.append(station.strip())
                if date_string:
                    datetime_var = datetime.datetime.strptime(date_string.group(), '%b%d')
                    date = datetime.datetime(year, datetime_var.month, datetime_var.day)

                # extracting station name
                station_name_match = re.search(r'^[A-Z]+', station)
                if station_name_match:
                    station_name = station_name_match.group()
                    station_name_list.append(station_name)
                else:
                    station_name_list.append(None)

                # extracting Pg
                station_pg_time_match = re.search(r'ePg\s+\d+\.\d+', station)

                if station_pg_time_match and date is not None:
                    time_text = station_pg_time_match.group().replace('ePg', '').strip()
                    station_pg_time_var = datetime.datetime.strptime(time_text, '%H%M%S.%f')

                    station_pg_time = datetime.datetime(year,
                                                        date.month,
                                                        date.day,
                                                        station_pg_time_var.hour,
                                                        station_pg_time_var.minute,
                                                        station_pg_time_var.second,
                                                        station_pg_time_var.microsecond)
                    station_pg_list.append(station_pg_time)
                else:
                    station_pg_list.append(None)

                # extracting Sg
                station_sg_time_match = re.search(r'eSg\s+\d+\.\d+', station)

                if station_sg_time_match and date is not None:

                    time_text = station_sg_time_match.group().replace('eSg', '').strip()
                    station_sg_time_var = datetime.datetime.strptime(time_text, '%H%M%S.%f')

                    station_sg_time = datetime.datetime(year,
                                                        date.month,
                                                        date.day,
                                                        station_sg_time_var.hour,
                                                        station_sg_time_var.minute,
                                                        station_sg_time_var.second,
                                                        station_sg_time_var.microsecond)
                    station_sg_list.append(station_sg_time)
                else:
                    station_sg_list.append(None)

        if not correct_station_lines_present:
            return

        # extracting date
        date = None

        date_string = re.search(r'[A-Z]+[0-9]+', record[0])

        if date_string:
            datetime_var = datetime.datetime.strptime(date_string.group(), '%b%d')
            date = datetime.datetime(year, datetime_var.month, datetime_var.day)

        # extracting date and time, if event has time

        date_string = re.search(r'[A-Z]+[0-9]+\s+\d+\.\d+', record[0])

        if date_string:
            datetime_var = datetime.datetime.strptime(date_string.group(), '%b%d %H%M%S.%f')
            date = datetime.datetime(year,
                                     datetime_var.month,
                                     datetime_var.day,
                                     datetime_var.hour,
                                     datetime_var.minute,
                                     datetime_var.second,
                                     datetime_var.microsecond)

        # extracting country

        country = None
        test = re.search(r'\.\d+\s+(.+)\(\d+\)', record[0])
        if test:
            country = re.sub(r'[.\d()]', '', test.group()).strip()

        # extracting latitude and longitude

        lat = None
        lon = None

        if re.search(r'\d+.\d+N', record[0]):
            lat = float(re.search(r'\d+.\d+N', record[0]).group().replace('N', ''))

        if re.search(r'\d+.\d+E', record[0]):
            lon = float(re.search(r'\d+.\d+E', record[0]).group().replace('E', ''))

        # extracting location_id
        location_id = None
        location_match = re.search(r'\((\d+)\)', record[0])

        if location_match:
            location_id = int(location_match.group().replace('(', '').replace(')', ''))

        # creating DataFrame with information about stations

        # creating table

        # creating dictionary and DataFrame and adding record to a record list

        arrival_times = {
            'station': station_name_list,
            'pg_arrival_time': station_pg_list,
            'sg_arrival_time': station_sg_list
        }
        station_data_frame = pandas.DataFrame(arrival_times)
        if not station_data_frame.empty:
            record_dictionary = {'time': date,
                                'lat': lat,
                                'lon': lon,
                                'country': country,
                                'location_id': location_id,
                                'arrival_times': station_data_frame}

            self._records.append(record_dictionary)

    def parse(self):
        file = open(self.path, 'r')

        for i in range(4):
            file.readline()

        # extracting year of a file
        year = int(re.search(r'\b\d{4}\b', file.readline()).group())

        file.readline()
        file.readline()
        record = []

        for line in file:
            if line == 'Copyright (c) Institute of Geophysics CAS Prague\n':
                break
            if line == '\n':
                self.addRecord(record, year)
                record = []
                continue

            record.append(line)


if __name__ == '__main__':
    pars = Parser('2023_02_bul.txt')
    pars.parse()
    for rec in pars.records:
        print(rec)
