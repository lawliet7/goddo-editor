import os
import pathlib


def root_folder_path() -> pathlib.Path:
    return goddo_test_folder_path().parent


def goddo_test_folder_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent


def assets_folder_path() -> pathlib.Path:
    return goddo_test_folder_path().joinpath('../assets')


def video_folder_path() -> pathlib.Path:
    return assets_folder_path().joinpath('videos')


def my_test_output_folder_path() -> pathlib.Path:
    return assets_folder_path().joinpath('.output')


def path_to_str(path: pathlib.Path):
    return str(path.resolve())


def list_files(path: pathlib.Path, filter_func=None):
    output_list = []
    for root, subFolder, files in os.walk(str(path.resolve())):
        for file in files:
            path_as_str = str(os.path.join(root, file))
            if filter_func:
                if filter_func(path_as_str):
                    output_list.append(path_as_str)
            else:
                output_list.append(path_as_str)
    return output_list


def str_to_path(str_path):
    return pathlib.Path(str_path)
