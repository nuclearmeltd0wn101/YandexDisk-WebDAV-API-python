from urllib import request, error
from urllib.parse import unquote
from datetime import datetime
from os.path import dirname
from yadisk.generic_entity import GenericEntity
from yadisk.file_entity import FileEntity


class DirectoryEntity(GenericEntity):
    @staticmethod
    def from_data(api, data, path, mandatory_refresh=True):
        if isinstance(data, dict):
            if "file_url" in data['d:propstat']['d:prop']:
                return FileEntity(api, path, data, mandatory_refresh)
            else:
                return DirectoryEntity(api, path, [data], mandatory_refresh)
        if isinstance(data, list):
            return DirectoryEntity(api, path, data, mandatory_refresh)

        raise NotImplementedError

    def __init__(self, api, path, data=None, mandatory_refresh=True):
        super().__init__(api, path, data)
        self._mandatory_refresh = mandatory_refresh
        self.__self = None
        self._items = None
        self._data_id = None

    def __str__(self):
        return f"<DirectoryEntity: {self.name} (" \
            + f"at {self._api.username}@YandexDisk: {self.path})>"

    def _data(self, should_refresh=False):
        must_refresh = self._mandatory_refresh and should_refresh
        if must_refresh:
            self._mandatory_refresh = False
        data = super()._data(must_refresh)

        if isinstance(data, dict):
            data = [data]

        if self._data_id is not id(data):
            self._data_id = id(data)
            self._items = list()
            selfpaths = (self._path, self._path + "/")

            for entity_data in data:
                path = unquote(entity_data['d:href'])
                if path in selfpaths:
                    self.__self = entity_data
                    continue
                entity = DirectoryEntity.from_data(
                    self._api, entity_data, path)
                self._items.append(entity)

        return data

    @property
    def _self(self):
        if not self.__self:
            self._data()
        return self.__self

    @property
    def items(self):
        if self._items == None or self._mandatory_refresh:
            self._data(True)
        return self._items
