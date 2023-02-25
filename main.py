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

            # checking if it is line about stations
            if 'eSg' in line or 'ePg' in line:

                correct_station_lines_present = True

                # extracting station name
                split_line = line.split()

                station_name_list.append(split_line[0])

                # extracting ePg and eSg
                station_sg_time = None
                station_pg_time = None

                if split_line[1] == 'ePg':
                    station_pg_time_var = datetime.datetime.strptime(split_line[2].replace(',', ''), '%H%M%S.%f')
                    station_pg_time = datetime.datetime(year,
                                                        date.month,
                                                        date.day,
                                                        station_pg_time_var.hour,
                                                        station_pg_time_var.minute,
                                                        station_pg_time_var.second,
                                                        station_pg_time_var.microsecond)

                elif split_line[1] == 'eSg':
                    station_sg_time_var = datetime.datetime.strptime(split_line[2].replace(',', ''), '%H%M%S.%f')
                    station_sg_time = datetime.datetime(year,
                                                        date.month,
                                                        date.day,
                                                        station_sg_time_var.hour,
                                                        station_sg_time_var.minute,
                                                        station_sg_time_var.second,
                                                        station_sg_time_var.microsecond)

                if len(split_line) > 3:

                    if split_line[3] == 'ePg':
                        station_pg_time_var = datetime.datetime.strptime(split_line[4].replace(',', ''), '%H%M%S.%f')
                        station_pg_time = datetime.datetime(year,
                                                            date.month,
                                                            date.day,
                                                            station_pg_time_var.hour,
                                                            station_pg_time_var.minute,
                                                            station_pg_time_var.second,
                                                            station_pg_time_var.microsecond)

                    elif split_line[3] == 'eSg':

                        station_sg_time_var = datetime.datetime.strptime(split_line[4].replace(',', ''), '%H%M%S.%f')
                        station_sg_time = datetime.datetime(year,
                                                            date.month,
                                                            date.day,
                                                            station_sg_time_var.hour,
                                                            station_sg_time_var.minute,
                                                            station_sg_time_var.second,
                                                            station_sg_time_var.microsecond)
                station_sg_list.append(station_sg_time)
                station_pg_list.append(station_pg_time)

            # checking if it is first line without any info, only with date and location_id
            elif '*' in line:
                # delete redundant characters
                split_line = line.replace('(', '').replace(')', '').replace('*', '').split()

                # extracting month, day and location_id
                datetime_var = datetime.datetime.strptime(split_line[0], '%b%d')

                date = datetime.datetime(year, datetime_var.month, datetime_var.day)

                location_id = int(split_line[1])

            # adding record to list if it has lines with correct format
            elif file_line == '\n':
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

            elif line == 'Copyright (c) Institute of Geophysics CAS Prague':
                break

            # checking if it is first line of record with additional info
            elif file_line[0] != ' ':

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

                # extracting country and location_id
                country = ''
                checkpoint = 3   # from what point of line start extracting coordinates
                for index, word in enumerate(split_line[2:]):
                    if '(' in word:
                        location_id = int(word.split('(')[1].replace(')', ''))
                        word = word.split('(')[0]
                        checkpoint += index
                        country += word
                        break
                    country += word + ' '

                country = country.strip()

                # extracting latitude and longitude
                if 'N' in split_line[checkpoint]:
                    lat = float(split_line[checkpoint].replace('N', ''))
                if 'E' in split_line[checkpoint + 1]:
                    lon = float(split_line[checkpoint + 1].replace('E', ''))

        file.close()


if __name__ == '__main__':
    pars = Parser('2023_02_bul.txt')
    pars.parse()
    for rec in pars.records:
        print(rec)
