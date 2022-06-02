from urllib import request, error
from urllib.parse import unquote
from datetime import datetime
import posixpath


class GenericEntity:
    def __init__(self, api, path: str,
                 data=None, mandatory_refresh: bool = True):
        self._api = api
        self._path = path
        self.__data = data
        self._data_id = id(data)

    def _data(self, must_refresh: bool = False) -> dict:
        # data retrieve lazyness
        if must_refresh or not self.__data:
            self.__data = self._api._get_entity(self._path)
            self._data_id = id(self.__data)

        return self.__data

    @property
    def _self(self):
        return self._data()

    def update_info(self) -> None:
        """
            Reload entity data from remote server
        """
        self.__data = None
        self._data()

    @property
    def path(self) -> str:
        """
            Remote entity absolute path
        """
        return unquote(self._self['d:href'])

    @property
    def name(self) -> str:
        """
            Remote entity name
        """
        return self._self['d:propstat']['d:prop']['d:displayname']

    @property
    def timestamp_created(self) -> datetime:
        """
            Entity creation timestamp as datetime
        """
        timestamp = self._self['d:propstat']['d:prop']['d:creationdate']
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

    @property
    def timestamp_modified(self) -> datetime:
        """
            Entity last modified timestamp as datetime
        """
        timestamp = self._self['d:propstat']['d:prop']['d:getlastmodified']
        return datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT')

    def move(self, destination_path: str) -> None:
        """
            Moves entity to specified path
        """
        if posixpath.realpath(posixpath.join("/", destination_path)) == "/":
            raise ValueError("Destination path cannot be root directory")

        self._api.move(self.path, destination_path)

        self._path = destination_path
        self.__data = None
        self._data(True)

    def rename(self, new_name: str) -> None:
        """
            Renames entity to specified name
            * Works as move if absolute path is submitted instead of new name
        """
        if self.path == "/":
            raise ValueError("Cannot rename root directory")
        path = self.path if self.path[-1] != "/" else self.path[:-1]
        basedir = posixpath.dirname(path)
        new_path = posixpath.join(basedir, new_name)
        new_path = posixpath.realpath(new_path)
        if new_path == basedir or new_path == path:
            raise ValueError("Invalid new name submitted")
        self.move(new_path)
