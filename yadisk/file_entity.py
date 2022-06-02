from urllib import request, error
from urllib.parse import unquote
from datetime import datetime
from os.path import dirname
from yadisk.generic_entity import GenericEntity


class FileEntity(GenericEntity):
    def __str__(self):
        return f"<FileEntity: {self.name} " \
            + f"(size: {self.size_bytes} bytes, " \
            + f"MIME: {self.mime_type}, " \
            + f"at {self._api.username}@YandexDisk: {self.path})>"

    @property
    def link(self) -> str:
        """
            Direct download link
        """
        return self._data()['d:propstat']['d:prop']['file_url']

    def save(self, path: str = None) -> None:
        """
            Saves file locally to specified path.
            If path is not specified, saves to current work directory with its remote name.
        """
        if not path:
            path = self.name
        request.urlretrieve(self.link, path)

    def get_data(self) -> bytes:
        """
            Retrieves the whole (beware of memory overflow on large files!) file and returns it as bytes
        """
        with request.urlopen(self.link) as response:
            return response.read()

    @property
    def size_bytes(self) -> int:
        """
            File size in bytes
        """
        return int(self._data()['d:propstat']['d:prop']['d:getcontentlength'])

    @property
    def mime_type(self) -> str:
        """
            File MIME type
        """
        return self._data()['d:propstat']['d:prop']['d:getcontenttype']
