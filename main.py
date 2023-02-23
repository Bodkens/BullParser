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

    def parse(self):
        file = open(self.path, 'r')

        for i in range(4):
            file.readline()

        # extracting year of a file
        year_line = file.readline().strip().split()
        year = int(year_line[0])

        file.readline()
        file.readline()

        station_name_list = []
        station_pg_list = []
        station_sg_list = []

        correct_station_lines_present = False
        date = None
        country = None
        lat = None
        lon = None
        location_id = None
        for file_line in file:
            line = file_line.strip()
            if line == 'Copyright (c) Institute of Geophysics CAS Prague\n':
                break
            # checking if it is first line without any info, only with date and location_id
            if re.search(r'^[A-Z]+[0-9]+\s+[*]+\(\d+\)', line):

                # delete redundant characters
                split_line = re.sub(r'[()*]', '', line).split()

                # extracting month, day and location_id
                datetime_var = datetime.datetime.strptime(split_line[0], '%b%d')

                date = datetime.datetime(year, datetime_var.month, datetime_var.day)

                location_id = int(split_line[1])

                continue

            # checking if it is first line of record with additional info
            if re.search(r'^[A-Z]+[0-9]+(.+)\(\d+\)', line):

                # extracting month, day and time

                split_line = line.split()

                month_day = datetime.datetime.strptime(split_line[0], '%b%d')

                time_var = datetime.datetime.strptime(split_line[1], '%H%M%S.%f')

                date = datetime.datetime(year,
                                         month_day.month,
                                         month_day.day,
                                         time_var.hour,
                                         time_var.minute,
                                         time_var.second,
                                         time_var.microsecond)

                # extracting country
                country_match = re.search(r'\.\d+\s+(.+)\(\d+\)', line)
                if country_match:
                    country = re.sub(r'[.\d()]', '', country_match.group()).strip()

                # extracting latitude and longitude
                lat_match = re.search(r'\d+.\d+N', line)
                if lat_match:
                    lat = float(lat_match.group().replace('N', ''))

                lon_match = re.search(r'\d+.\d+E', line)
                if lon_match:
                    lon = float(lon_match.group().replace('E', ''))

                # extracting location_id
                location_match = re.search(r'\((\d+)\)', line)

                if location_match:
                    location_id = int(location_match.group().replace('(', '').replace(')', ''))

                continue

            # checking if it is line about stations

            if re.search(r'[A-Z]+\s+e(Pg)|(Sg)+\s+\d+\.\d+', line):
                correct_station_lines_present = True
                # extracting station name

                split_line = line.split()

                station_name_list.append(split_line[0])

                # extracting Pg
                station_pg_time_match = re.search(r'ePg\s+\d+\.\d+', line)

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
                station_sg_time_match = re.search(r'eSg\s+\d+\.\d+', line)

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

            # adding record to list if it has lines with correct format
            if file_line == '\n':
                if correct_station_lines_present:
                    arrival_times = {
                        'station': station_name_list,
                        'pg_arrival_time': station_pg_list,
                        'sg_arrival_time': station_sg_list
                    }
                    station_data_frame = pandas.DataFrame(arrival_times)
                    record_dictionary = {
                        'time': date,
                        'lat': lat,
                        'lon': lon,
                        'country': country,
                        'location_id': location_id,
                        'arrival_times': station_data_frame}

                    self._records.append(record_dictionary)

                station_name_list = []
                station_pg_list = []
                station_sg_list = []
                correct_station_lines_present = False
                date = None
                country = None
                lat = None
                lon = None
                location_id = None
        file.close()


if __name__ == '__main__':
    pars = Parser('2023_02_bul.txt')
    pars.parse()
    for rec in pars.records:
        print(rec)

