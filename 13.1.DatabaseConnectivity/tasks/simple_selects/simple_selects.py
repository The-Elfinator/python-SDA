import typing as tp
import sqlite3


class DataBaseHandler:
    _cursor: sqlite3.Cursor

    def __init__(self, sqlite_database_name: str):
        """
        Initialize all the context for working with database here
        :param sqlite_database_name: path to the sqlite3 database file
        """
        connection = sqlite3.connect(sqlite_database_name)
        self._cursor = connection.cursor()

    def get_most_expensive_track_names(self, number_of_tracks: int) -> tp.Sequence[tuple[str]]:
        """
        Return the sequence of track names sorted by UnitPrice descending.
        If the price is the same, sort by TrackId ascending.
        :param number_of_tracks: how many track names should be returned
        keywords: SELECT, ORDER BY, LIMIT
        :return:
        """
        self._cursor.execute("SELECT Name FROM tracks ORDER BY UnitPrice DESC, TrackId ASC LIMIT :limit",
                             {'limit': f'{number_of_tracks}'})
        return self._cursor.fetchall()

    @staticmethod
    def _get_genres(genres: tp.Sequence[str]) -> str:
        ret = ""
        for i in range(len(genres)):
            ret += "'" + genres[i] + "'"
            if i != len(genres) - 1:
                ret += ", "
        return ret

    def get_tracks_of_given_genres(self, genres: tp.Sequence[str], number_of_tracks: int) -> tp.Sequence[tuple[str]]:
        """
        Return the sequence of track names that have one of the given genres
        sort asending by track duration and limit by number_of_tracks
        :param number_of_tracks:
        :param genres:
        keywords: JOIN, WHERE, IN
        :return:
        """
        print(self._get_genres(genres))
        req = "SELECT tracks.Name FROM tracks " + \
              "JOIN genres on tracks.GenreId=genres.GenreId " + \
              "WHERE genres.Name in (" + self._get_genres(genres) + ") " + \
              "ORDER BY tracks.Milliseconds ASC " + \
              "LIMIT " + str(number_of_tracks)
        self._cursor.execute(req)
        return self._cursor.fetchall()

    def get_tracks_that_belong_to_playlist_found_by_name(self, name_needle: str) -> tp.Sequence[tuple[str, str]]:
        """
        Return a sequence of track names and playlist names such that the track belongs to the playlist and
        the playlist's name contains `name_needle` (case sensitive).
        If the track belongs to more than one suitable playlist it
        should occur in the result for each playlist, but not just once
        :param name_needle:
        keywords: JOIN, WHERE, LIKE
        :return:
        """
        self._cursor.execute("SELECT tracks.Name, playlists.Name FROM tracks "
                             "JOIN playlist_track on playlist_track.TrackId=tracks.TrackId "
                             "JOIN playlists on playlist_track.PlaylistId=playlists.PlaylistId "
                             "WHERE playlists.Name LIKE :required",
                             {
                                 'required': f'%{name_needle}%'
                             })
        return self._cursor.fetchall()

    def teardown(self) -> None:
        """
        Cleanup everything after working with database.
        Do anything that may be needed or leave blank
        :return:
        """
        self._cursor.close()
