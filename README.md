# Yandex.Disk WebDAV API Python 3 library

## Current library capabilities
* Read content and metadata from remote server
* Move and rename entities (files and directories)

## Dependencies:
* Python 3
* xmltodict

Install with:
`pip install -r requirements.txt`

## Main API usage:
```
from yadisk.api import YandexDisk
api = YandexDisk("you username here", "your app password here")
```

**Don't even try to log in with your account password** - use [*application password*](https://yandex.ru/support/id/authorization/app-passwords.html) instead:



In this particular case, you need to create a password *with application type "disk"*.

During main API entity initialization authorization test occurs.
If it's failed, **PermissionError** raises.


During API usage various errors may occur.
You should handle it by your own from **NotImplementedError**, as *this API handles the very basic cases*.

Once you'd initialized main API entity, you may use it.

There are method and properties available:
* api.username: str - logged in account username
* api.space_used_bytes: int - remote storage used space in bytes
* api.space_available_bytes: int - remote storage available (free) space in bytes

* api.get_entity(path="/") -> GenericEntity - retrieves entity information and encapsulates it into either **FileEntity** either **DirectoryEntity** wrapper classes. If no path submitted, retrieves root directory information.


May raise exceptions:

**FileNotFoundError** if no such file or directory at specified path on remote server
 

* move(source_path, destination_path, allow_overwrite=False) - moves entity with source_path to destination_path. Destination path base dir must exist. Use allow_overwrite to decide, whether destination overwrite is allowed (default: False)

May raise exceptions:

**FileNotFoundError** if source entity not exists

**FileExistsError** if destination entity exists already and overwrite is not allowed

**NotADirectoryError** if destination entity path base directory not exists

## GenericEntity
This is a base class for **FileEntity** and **DirectoryEntity**, so every method or property it has, so does its childs.

If not retrieved from api.get_entity, it retrieves data from server **lazily**.
That means no request will occur until data will be requested for the first time.

Let's say, we'd retrieved a root directory entity:
`root = api.get_entity("/")`

There's methods and properties it has from GenericEntity:
* root.path: str - remote entity absolute path
* root.name: str - remote entity name
* root.timestamp_created: datetime.datetime - entity creation timestamp 
* root.timestamp_modified: datetime.datetime - entity last modifed timestamp
* root.update_info() - reload entity data from remote server
* root.move(destination_path) - move entity to destination path

Raises almost the same exceptions as api.move, but:
Can raise **ValueError** if destination path is root directory

* root.rename(new_name) - moves entity into one with a new name at the same base directory

Raises almost the same exceptions as root.move, but:

Can raise **ValueError** if entity is root directory or attepted to rename into itself, or any other inappropriate rename attempts happens.

## DirectoryEntity
This is a wrapper entity class for remote directory.

Aside of GenericEntity methods and properties it has only one, but a crucial property:
* root.items - responses with list of child entities (subfiles, subfolders)

## FileEntity
This is a wrapper entity class for remote file

Let's suppose, your remote drive has file /foo/bar.png

You can retrieve its wrapper entity with
`file_entity = api.get_entity("/foo/bar.png")`

Aside of GenericEntity methods and properties it has these onces:
* file_entity.size_bytes: int - file size in bytes
* file_entity.link: str - direct download link, which requires no authorization
* file_entity.mime_type: str - file MIME type
* file_entity.save(path) - saves file locally to specified path. If no path provided, it will be downloaded to current work dir with its remote name
* file_entity.get_data(): bytes - retrieves file and returns its content as byte string. Beware of memory overflow on large files!
