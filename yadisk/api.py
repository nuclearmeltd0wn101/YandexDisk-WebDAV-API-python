from urllib import request, error
from urllib.parse import urljoin, quote
from xmltodict import parse
from yadisk.generic_entity import GenericEntity
from yadisk.directory_entity import DirectoryEntity

import posixpath


class YandexDisk:
    BASE_URL = "https://webdav.yandex.ru"

    def __init__(self, username: str, password: str):
        self._username = username
        keychain = request.HTTPPasswordMgrWithDefaultRealm()
        keychain.add_password(None, self.BASE_URL, username, password)
        handler = request.HTTPBasicAuthHandler(keychain)
        self._opener = request.build_opener(handler)
        try:
            self._request("/")
        except PermissionError as e:
            raise

    def __str__(self):
        return f"<YandexDisk API: User {self.username}, " \
            + f"Space: Used {self.space_used_bytes} bytes, " \
            + f"Available: {self.space_available_bytes} bytes>"

    @property
    def username(self) -> str:
        return self._username

    def _request(self, path: str, method: str = "PROPFIND",
                 body: bytes = b"", headers: dict = None) -> bytes:
        if not headers:
            headers = {
                "Depth": 1
            }

        url = urljoin(self.BASE_URL, quote(str(path)))
        req = request.Request(url, method=method,
                              headers=headers, data=body)
        try:
            response = self._opener.open(req)
            return response.read()

        except error.HTTPError as e:
            if e.code == 401:
                raise PermissionError("Authentication failure")
            raise

    def _get_entity(self, path: str):
        try:
            response = self._request(path)
        except error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError

            raise NotImplementedError("Status code {e.code}")

        data = parse(response)
        return data['d:multistatus']['d:response']

    def get_entity(self, path: str = "/") -> GenericEntity:
        """
            Retrieve entity information from remote server.
            If path isn't specified, retrieves root directory
        """
        path = posixpath.realpath(posixpath.join("/", path))
        data = self._get_entity(path)
        return DirectoryEntity.from_data(self, data, path, False)

    def move(self, source_path: str,
             destination_path: str, allow_overwrite: bool = False) -> None:
        """
            Moves entity with source_path to destination_math
            Destination path base dir must exist
            Use allow_overwrite to decide, whether destination overwrite is allowed (default: False)
        """
        source_path = posixpath.realpath(posixpath.join("/", source_path))
        destination_path = posixpath.realpath(
            posixpath.join("/", destination_path))

        headers = {
            "Overwrite": "T" if allow_overwrite else "F",
            "Destination": destination_path
        }

        try:
            self._request(source_path, method="MOVE", headers=headers)
        except error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"{source_path} not found")
            if e.code == 412:
                raise FileExistsError(f"{destination_path} exists already")
            if e.code == 409:
                raise NotADirectoryError(
                    f"{destination_path} contains nonexistent directory")

            raise NotImplementedError(f"Server returned status code {e.code}")

    def _get_space_info(self) -> dict:
        body = """<D:propfind xmlns:D="DAV:">
  <D:prop>
    <D:quota-available-bytes/>
    <D:quota-used-bytes/>
  </D:prop>
</D:propfind>""".encode("utf-8")

        response = self._request("/", body=body)
        data = parse(response)
        return data['d:multistatus']['d:response'][0]['d:propstat']['d:prop']

    @property
    def space_used_bytes(self) -> int:
        """
            Remote storage used space in bytes
        """
        return int(self._get_space_info()['d:quota-used-bytes'])

    @property
    def space_available_bytes(self) -> int:
        """
            Remote storage available (free) space in bytes
        """
        return int(self._get_space_info()['d:quota-available-bytes'])
