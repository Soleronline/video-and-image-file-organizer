import datetime
import mimetypes
import os
import shutil
import time

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from typing import Union
from random import random

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from simple_file_checksum import get_checksum

ACTION_NOTHING = 0
ACTION_MOVE = 1
ACTION_COPY = 2

IMAGE = "img"
VIDEO = "vid"
PATH_DST = "imgs_moved"


class InfoFiles(BaseModel):
    directories: int = 0
    files_count: int = 0
    files_image: int = 0
    files_video: int = 0
    files_unknown: int = 0
    files_without_date_creation: int = 0

    def update(self, tmp: "InfoFiles") -> None:
        self.directories += tmp.directories
        self.files_count += tmp.files_count
        self.files_image += tmp.files_image
        self.files_video += tmp.files_video
        self.files_unknown += tmp.files_unknown
        self.files_without_date_creation += tmp.files_without_date_creation

    def print(self) -> None:
        print(f"\nDirectories found: {self.directories}")
        print(f"Files found: {self.files_count}")
        print(f"Files of type other than image or video: {self.files_unknown}")
        print(f"Image type files: {self.files_image}")
        print(f"Video type files: {self.files_video}")
        print("Image or video type files without creation date:", end="")
        print(f"{self.files_without_date_creation}")


def get_file_type(path_file: str) -> str:
    file_type = mimetypes.guess_type(path_file)
    if file_type[0]:
        if "image" in file_type[0]:
            return IMAGE
        if "video" in file_type[0]:
            return VIDEO
    return ""


def get_date_creation_for_image(
        filename: str) -> Union[datetime.datetime, None]:
    DATE_TIME = 0x0132
    DATE_TIME_ORIG_TAG = 36867
    TAG_ID = 306

    date_creation = None
    print("filename", filename)
    try:
        im = Image.open(filename)
    except ValueError:
        return date_creation
    except UnidentifiedImageError:
        return date_creation
    exif = im._getexif()
    exifdata = im.getexif()
    im.close()

    if exif:
        date_creation = exif.get(DATE_TIME, exif.get(DATE_TIME_ORIG_TAG, None))

    if date_creation is None and exifdata:
        date_creation = exifdata.get(TAG_ID, None)

    if date_creation:
        return datetime.datetime.strptime(date_creation.split()[0], "%Y:%m:%d")

    return date_creation


def get_date_creation_for_video(
        filename: str) -> Union[datetime.datetime, None]:
    date_creation = None
    parser = createParser(filename)
    if parser:
        with parser:
            try:
                metadata = extractMetadata(parser)
            except Exception as err:
                print(f"Metadata extraction error: {err} for {filename}")
                metadata = None
        if metadata:
            export_dict = metadata.exportDictionary()
            date_creation = export_dict["Metadata"]["Creation date"]

    if date_creation:
        return datetime.datetime.strptime(date_creation.split()[0], "%Y-%m-%d")
    return date_creation


def get_new_filename(filename: str, path_dst: str) -> str:
    """
    For a filename (full path of the file) and destination directory
    it calculates the hash of the file and returns the name of the file formed
    by:
        hash + el nombre del fichero + extension

    If the file name exists in the destination directory, add a random
    to return a unique name

    return:
        str: filename
    """
    MAX_LEN_FILENAME = 250
    name, extension = split_filename(filename)
    hash = get_checksum(filename)
    new_filename = f"{hash}_{name}"[:MAX_LEN_FILENAME]
    new_filename += f".{extension}"
    full_path = os.path.join(path_dst, f"{new_filename}")
    while os.path.isfile(full_path):
        new_filename = f"{hash}_{get_name_random()}_{name}"[:MAX_LEN_FILENAME]
        new_filename += f".{extension}"
        full_path = os.path.join(path_dst, f"{new_filename}")
    return new_filename


def get_name_random() -> str:
    """
    Calculates a random string formed by the timestamp + a random number
    """
    return f"_{int(time.time() * 10000)}_{int(random()*10000)}"


def split_filename(filename: str) -> tuple:
    """
    For a complete path of a file, returns a tuple formed
    (
        name of the file without the path of where it was,
        file extension
    )
    """
    tmp = filename.split(".")
    extension = tmp[-1]
    file_name = ".".join(tmp[:-1])
    name = file_name.split(os.path.sep)[-1]
    return (name, extension)


def move_file(
    filename_src: str,
    dirpath_dst: str,
    filename_dst: str,
    action: int = ACTION_MOVE
) -> None:
    os.makedirs(dirpath_dst, exist_ok=True)
    if action == ACTION_MOVE:
        shutil.move(filename_src, os.path.join(dirpath_dst, filename_dst))
    elif action == ACTION_COPY:
        shutil.copy2(filename_src, os.path.join(dirpath_dst, filename_dst))
    else:
        raise Exception("Action unknown")


def organization_file(
    directory: str,
    directory_dst: str = PATH_DST,
    action: int = ACTION_NOTHING,
    show_process: bool = False
) -> InfoFiles:
    info_files = InfoFiles()
    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        if os.path.isdir(full_filename):
            info_files.directories += 1
            info_files.update(organization_file(
                full_filename, directory_dst, action, show_process))
            continue

        info_files.files_count += 1
        file_type = get_file_type(full_filename)
        if file_type == IMAGE:
            info_files.files_image += 1
            date_creation = get_date_creation_for_image(full_filename)
        elif file_type == VIDEO:
            info_files.files_video += 1
            date_creation = get_date_creation_for_video(full_filename)
        else:
            info_files.files_unknown += 1
            continue

        if date_creation is None:
            info_files.files_without_date_creation += 1
            continue

        if action != ACTION_NOTHING:
            path_dst = os.path.join(
                directory_dst,
                str(date_creation.year),
                str(date_creation.month)
            )
            new_filename = get_new_filename(full_filename, path_dst)

            if show_process:
                print(full_filename, " -> ", path_dst, new_filename)
            move_file(full_filename, path_dst, new_filename, action)
        elif show_process:
            print(".", end="", flush=True)

    return info_files
