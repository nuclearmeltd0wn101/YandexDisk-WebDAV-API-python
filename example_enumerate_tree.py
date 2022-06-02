from yadisk.api import YandexDisk
from yadisk.directory_entity import DirectoryEntity
from yadisk.file_entity import FileEntity

# paste your ussername and app password in secret.py
from secret import username, password


def __main__():
    print("Connecting..")
    try:
        api = YandexDisk(username, password)
    except PermissionError:
        print("Login failed. Invalid credentials submitted")
        return

    used_in_mib = api.space_used_bytes / 2 ** 20
    available_in_mib = api.space_available_bytes / 2 ** 20
    print(f"Successfully logged in as {api.username}")
    print(f"Remote drive usage: {used_in_mib:.2f} MiB used, "
          + f"{available_in_mib:.2f} Mib available")
    print("Enumerating remote drive tree..\n")

    root = api.get_entity()  # equals to get_entity("/")

    count = 0
    stack = [root]
    while stack:
        count += 1
        entity = stack.pop()
        if isinstance(entity, FileEntity):
            size_in_mib = entity.size_bytes / 2 ** 20
            print(f"{entity.path} -- is file: size {size_in_mib:.2f} MiB, "
                  + f"MIME type: {entity.mime_type}")
        if isinstance(entity, DirectoryEntity):
            print(f"{entity.path} -- is directory")
            for child in entity.items:
                stack.append(child)

    print(f"\nTotal {count} files and directories found")


if __name__ == "__main__":
    __main__()
