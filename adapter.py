"""

"""

import datetime
import gc
import os
import re

import pandas as pd
import unidecode

from enum import Enum


class EventType(Enum):

    NONE = 'NONE'
    EXPLOSION = 'E'
    TECTONIC_EVENT = 'T'
    MINING_EVENT = 'M'


class Country(Enum):

    NONE = 'NONE'
    AU = 'AU'
    CZ = 'CZ'
    GE = 'GE'
    PL = 'PL'
    SK = 'SK'


_INFO_DICT = {
    'belchatow':            {'country': Country.PL,   'type': EventType.MINING_EVENT,   'location': 'belchatow'},
    'exp':                  {'country': Country.NONE, 'type': EventType.EXPLOSION,      'location': ''},
    'hronov':               {'country': Country.CZ,   'type': EventType.MINING_EVENT,   'location': 'hronov'},
    'jesenik':              {'country': Country.CZ,   'type': EventType.TECTONIC_EVENT, 'location': 'jesenik'},
    'kromeriz':             {'country': Country.CZ,   'type': EventType.TECTONIC_EVENT, 'location': 'kromeriz'},
    'kraliky':              {'country': Country.CZ,   'type': EventType.TECTONIC_EVENT, 'location': 'kraliky'},
    'okcb':                 {'country': Country.CZ,   'type': EventType.MINING_EVENT,   'location': 'okcb'},
    'okr':                  {'country': Country.AU,   'type': EventType.MINING_EVENT,   'location': 'okr'},
    'poland - high tatras': {'country': Country.PL,   'type': EventType.TECTONIC_EVENT, 'location': 'hight tatras'},
    'poland - lubin':       {'country': Country.PL,   'type': EventType.MINING_EVENT,   'location': 'lubin'},
    'poland':               {'country': Country.PL,   'type': EventType.MINING_EVENT,   'location': ''},
    'orava':                {'country': Country.SK,   'type': EventType.TECTONIC_EVENT, 'location': 'orava'},
    'staric':               {'country': Country.CZ,   'type': EventType.MINING_EVENT,   'location': 'staric'},
    'tectonic event':       {'country': Country.NONE, 'type': EventType.TECTONIC_EVENT, 'location': ''},
    'west bohemia':         {'country': Country.CZ,   'type': EventType.MINING_EVENT,   'location': 'west bohemia'}
}

_LOCATION_DICT = {
    'bilcice':     {'country': Country.CZ, 'location': 'bilcice'},
    'bohucovice':  {'country': Country.CZ, 'location': 'bohucovice'},
    'hrabuvka':    {'country': Country.CZ, 'location': 'ostrava-hrabuvka'},
    'jakubcovice': {'country': Country.CZ, 'location': 'jakubcovice'},
    'kajlovec':    {'country': Country.CZ, 'location': 'kajlovec'},
    'slovakia':    {'country': Country.SK, 'location': ''},
    'germany':     {'country': Country.GE, 'location': ''},
    'lipno':       {'country': Country.CZ, 'location': 'lipno'},
    'dukla':       {'country': Country.SK, 'location': 'dukla'},
}


class BulletinParser(object):
    """

    """

    def __init__(self,
                 fn: str = None,
                 ignore_bad_lines: bool = False,
                 verbose: bool = False):
        """

        """

        self._str_year = None
        self._lst_events = []

        self._df_events = None

        self._file_bulletin = None
        self.file_bulletin = fn

        self._ignore_bad_lines = None
        self.ignore_bad_lines = ignore_bad_lines

        self._verbose = None
        self.verbose = verbose

    @property
    def file_bulletin(self) -> str:
        """

        """

        return self._file_bulletin

    @file_bulletin.setter
    def file_bulletin(self, fn: str) -> None:
        """

        """

        if fn == self._file_bulletin:
            return

        self.__reset()
        self._file_bulletin = fn

    @property
    def dataframe_events(self) -> pd.DataFrame:

        if self._df_events is None:
            self.__createDataframe()

        return self._df_events

    @property
    def ignore_bad_lines(self) -> bool:


        """

        """

        return self._ignore_bad_lines

    @ignore_bad_lines.setter
    def ignore_bad_lines(self, flg: bool) -> None:
        """

        """

        if self.ignore_bad_lines == flg:
            return

        self.__reset()
        self._ignore_bad_lines = flg

    @property
    def verbose(self) -> bool:
        """

        """

        return self._verbose

    @verbose.setter
    def verbose(self, flg: bool) -> None:

        self._verbose = flg

    def __reset(self) -> None:

        del self._lst_events; self._lst_events = None
        del self._df_events; self._df_events = None
        gc.collect()

    def __parse_row(self, row: str, n: int) -> dict:

        # since bulletin has many inconsistencies related to using tabulator, white spaces etc.
        # we have to split line using white spaces

        row_words = iter(row.split())
        event = {}

        only_only_atime = True if ('Pg' not in row and 'Sg' in row) or ('Pg' in row and 'Sg' not in row) else False
        date_found = False
        times_found = False

        for j, word in enumerate(row_words):

            # get date
            if re.search(r'^(\d+){,2}\.(\d+){,2}(\.)*', word):
                day, month = word.split('.')[:2]
                day = int(day)
                month = int(month)

                str_date = '20{}-{:02d}-{:02d}'.format(self._str_year, month, day)
                event['date'] = datetime.date.fromisoformat(str_date)

                date_found = True
            # process arrive time of primary wave
            elif re.search('[P,p]g', word) and date_found:
                time = next(row_words)
                str_date_time = '{} {}'.format(str_date, time)

                try:
                    event['pg_arrival_time'] = datetime.datetime.fromisoformat(str_date_time)
                except ValueError:
                    msg_err = 'Parsing error (arr. time pg)'
                    msg_err = '{}: {}:{}'.format(msg_err, os.path.basename(self.file_bulletin), n + 2)

                    if not self.ignore_bad_lines:
                        raise ValueError(msg_err)
                    elif self.verbose:
                        print(msg_err)

                    event = {}
                    break

                if only_only_atime: times_found = True
            # process arrive time of second wave
            elif re.search('[S,s]g', word) and date_found:
                time = next(row_words)
                str_date_time = '{} {}'.format(str_date, time)

                try:
                    event['sg_arrival_time'] = datetime.datetime.fromisoformat(str_date_time)
                except ValueError:
                    msg_err = 'Parsing error (arr. time sg)'
                    msg_err = '{}: {}:{}'.format(msg_err, os.path.basename(self.file_bulletin), n + 2)

                    if not self.ignore_bad_lines:
                        raise ValueError(msg_err)
                    elif self.verbose:
                        print(msg_err)

                    event = {}
                    break

                times_found = True
            # process info
            elif times_found:

                info = '{}'.format(word.lower())
                for info_word in row_words:
                    info = '{} {}'.format(info, info_word.lower())

                trusted = True
                if '?' in info:
                    trusted = False
                    info = info.replace('?', '')

                if ',' in info:
                    info = info.replace(',', r' -')

                if 'polsko' in info:
                    info = info.replace('polsko', 'poland')
                elif 'slovensko' in info:
                    info = info.replace('slovensko', 'slovakia')

                event['type'] = 'NONE'
                event['country'] = 'NONE'

                # remove accents
                event['info'] = unidecode.unidecode(info.strip())

                # flag related trusting a event type
                event['trusted'] = trusted

        # final row consistency check
        if not date_found or not times_found:
            msg_err = 'Any useful date information was not found'

            if not self.ignore_bad_lines:
                raise ValueError(msg_err)
            elif self.verbose:
                print(msg_err)

            event = None

        return event

    def __parse(self) -> list:

        if not os.path.exists(self.file_bulletin):
            raise IOError("Source file \'{}\' does not exist!".format(self.file_bulletin))

        # get year
        file_name = os.path.basename(self.file_bulletin)
        self._str_year = file_name.split('.')[0].split('_')[1]

        # process file
        fhandler = open(self.file_bulletin, encoding='utf-8')
        # skip station info
        next(fhandler)

        # obtain list of events
        event_list = []

        # process rows
        for i, row in enumerate(fhandler):

            if 'Pn' in row or 'Sn' in row:
                continue

            if 'Pg' not in row and 'Sg' not in row:

                if re.match(r'\s+', row):
                    msg = 'Empty line: {}:{}'.format(file_name, i + 2)

                    if not self.ignore_bad_lines:
                        raise ValueError(msg)
                    else:
                        print(msg)
                else:
                    msg = 'Wrong line format: {}:{}'.format(file_name, i + 2)

                    if not self.ignore_bad_lines:
                        raise ValueError(msg)
                    else:
                        print(msg)

                continue

            try:
                event = self.__parse_row(row, i)
            except ValueError:
                msg_err = 'Cannot process {}:{}'.format(file_name, i)

                if not self.ignore_bad_lines:
                    raise ValueError(msg_err)
                elif self.verbose:
                    print(msg_err)

                continue

            if event is not None: event_list.append(event)

        fhandler.close()

        return event_list

    @staticmethod
    def __determineLocation(info: str, country: str) -> (str, str):

        _info = info.replace('-', '').strip()
        location = ''

        for loc_key in _LOCATION_DICT:

            if loc_key in _info:

                location = _LOCATION_DICT[loc_key]['location']
                if country == 'NONE':
                    country = _LOCATION_DICT[loc_key]['country'].value
                break

        return country, location

    def __processInfo(self, info: str) -> (str, str, str):

        if info == '':
            return Country.NONE.value, EventType.NONE.value, ''

        found = False
        location = ''

        for key in list(_INFO_DICT.keys()):

            # processing info
            if key in info:

                entry = _INFO_DICT[key]

                type_event = entry['type']
                country = entry['country'].value
                location = entry['location']

                if 'tectonic event' in info:
                    _info = info.replace(key, '').strip()
                if 'poland -' in info:
                    _info = info.replace('poland -', '').strip()
                else:
                    _info = info.replace(key, '')

                # try to determine location
                if location == '' and _info != '':
                    country, location = self.__determineLocation(_info, country)

                found = True
                break

        if found:
            return type_event.value, country, location
        else:
            return 'NONE', 'NONE', ''

    def __createDataframe(self) -> None:

        if self._lst_events is None:
            self._lst_events = self.__parse()

        """
        TODO developer note
        """

        for event in self._lst_events:

            event_type, country, info = self.__processInfo(event['info'])

            # update event
            event['type'] = event_type
            event['country'] = country
            event['location'] = info

        # clean up
        if self._df_events is not None:
            del self._df_events

        self._df_events = pd.DataFrame.from_dict(self._lst_events)

        cols = ['date', 'pg_arrival_time', 'sg_arrival_time', 'type', 'country', 'location', 'trusted']
        self._df_events = self._df_events[cols]


class BulletinDataAdapter(object):

    def __init__(self,
                 list_bulletin_files: list[str],
                 ignore_bad_lines: bool = False,
                 verbose: bool = False):
        """

        """

        self._df_events = None

        self._lst_bulletins = []
        self.list_bulletins = list_bulletin_files

        self._ignore_bad_lines = None
        self.ignore_bad_lines = ignore_bad_lines

        self._verbose = None
        self.verbose = verbose

    @property
    def list_bulletins(self) -> list[str]:

        return self._lst_bulletins

    @list_bulletins.setter
    def list_bulletins(self, lst: list[str]) -> None:

        if self._lst_bulletins == lst:
            return

        self.__reset()
        self._lst_bulletins = lst

    @property
    def dataframe_events(self) -> pd.DataFrame:

        if self._df_events is not None:
            return self._df_events

        self.load()
        return self._df_events

    @property
    def ignore_bad_lines(self) -> bool:

        return self._ignore_bad_lines

    @ignore_bad_lines.setter
    def ignore_bad_lines(self, flg: bool) -> None:

        self._ignore_bad_lines = flg

    @property
    def verbose(self) -> bool:

        return self._verbose

    @verbose.setter
    def verbose(self, flg: bool) -> None:

        self._verbose = flg

    def __reset(self):

        del self._df_events; self._df_events = None
        gc.collect()

    def load(self) -> None:

        if self._df_events is not None:
            return

        lst_df = []
        parser = BulletinParser(
            ignore_bad_lines=self.ignore_bad_lines,
            verbose=self.verbose
        )

        # process each bulletin file
        for fn in self._lst_bulletins:

            parser.file_bulletin = fn

            # process file
            try:
                df = parser.dataframe_events
            except IOError and ValueError:
                msg = 'Cannot process file {}'.format(fn)

                if not self.ignore_bad_lines:
                    raise IOError(msg)
                elif self.verbose:
                    print(msg)

                continue

            lst_df.append(df)

        # check
        if len(lst_df) == 0:
            msg_err = 'Files {} do not contain any useful information'.format(*self._lst_bulletins)
            if not self.ignore_bad_lines:
                raise IOError(msg_err)
            elif self.verbose:
                print(msg_err)

        # create
        self._df_events = pd.concat(lst_df, ignore_index=True)

    def toSQL(self) -> None:

        pass

    def toPickle(self, fn: str) -> None:

        if self._df_events is None:
            self.load()

        if '.pkl' not in fn:
            fn = '{}.pkl'.format(fn)

        self._df_events.to_pickle(fn)

