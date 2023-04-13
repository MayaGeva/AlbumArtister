"""
The Album Artister program
Purpose: to set an album artist tag to song files missing it
"""
import argparse
import logging
import os
from pathlib import Path
from typing import List, Callable, Optional

import music_tag

ARTIST = "artist"
ALBUM_ARTIST = "album_artist"
TITLE = "title"
MP3 = ".mp3"


def fix_album_artist_tag(songs: List[music_tag.AudioFile]) -> None:
    """
    Fix missing album artist tag in songs list
    :param songs: A list of songs to be fixed
    """
    fixed_songs = 0
    for song in songs:
        if ALBUM_ARTIST not in song:
            set_album_artist(song)
            fixed_songs += 1
            print(f"Fixed missing tag in song: {song[TITLE]}")
    print(f"Finished fixing all songs ({fixed_songs} songs fixed)")


def set_album_artist(song: music_tag.AudioFile) -> None:
    """
    Set the album artist tag of the file to the value of the Artist tag
    :param song: The file to be modified
    """
    artist = song[ARTIST]
    song[ALBUM_ARTIST] = artist
    song.save()


def is_album_artist(song: music_tag.AudioFile) -> bool:
    """
    Check if exists a value of album artist tag in song
    :param song: The song object to be checked
    :return: True if the album artist exists, false otherwise
    """
    if ALBUM_ARTIST in song.tag_map:
        return True
    return False


def get_all_files(dir_path: Path, file_filter: Optional[Callable[[Path], bool]]) -> List[Path]:
    """
    Get all the files listed in the directory and its subdirectories
    :param dir_path: The base directory path
    :param file_filter: a filter for the files found
    :return: A list of paths to all the files listed in the directory
    """
    files: List[Path] = [dir_path.joinpath(file)
                         for file in os.listdir(dir_path)
                         if file_filter(dir_path.joinpath(file))]
    sub_dirs: List[Path] = [dir_path.joinpath(file)
                            for file in os.listdir(dir_path)
                            if dir_path.joinpath(file).is_dir()]
    for sub_dir in sub_dirs:
        full_path = dir_path.joinpath(sub_dir)
        files.extend(get_all_files(full_path, file_filter))
    return files


def load_all_songs(files: List[Path]) -> List[music_tag.AudioFile]:
    """
    Load all song objects from list of file paths
    :param files: The list of file paths to be loaded
    :return: A list of loaded song objects
    """
    songs: List[music_tag.AudioFile] = []
    for file_path in files:
        song = load_song(file_path)
        songs.append(song)
    return songs


def load_song(path: Path) -> music_tag.AudioFile:
    """
    Load a song object from a file path
    :param path: The file path of the song to be loaded
    :return: An audio file object of the loaded song
    """
    try:
        song = music_tag.load_file(path)
    except UnboundLocalError:
        print(f"File is not a music file: {path}")
    except NotImplementedError:
        print(f"File is not a music file: {path}")
    except PermissionError:
        print(f"Permission error: {path}")
    except Exception as e:
        print(f"Something went wrong: {e} Path: {path}")
    else:
        return song


def main():
    parser = argparse.ArgumentParser(description="Set the album artist tag of a music file")
    parser.add_argument("file_path", type=str, help="The path of the file to be modified")
    args = parser.parse_args()
    dir_path = Path(args.file_path)
    files = get_all_files(dir_path, lambda file_path: file_path.suffix == MP3)
    songs = load_all_songs(files)
    print(f"Finished scanning all files ({len(songs)} songs found)")
    fix_album_artist_tag(songs)


if __name__ == "__main__":
    main()
