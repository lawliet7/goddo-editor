import pathlib


def root_folder_path() -> pathlib.Path:
    return goddo_test_folder_path().parent


def goddo_test_folder_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent


def assets_folder_path() -> pathlib.Path:
    return goddo_test_folder_path().joinpath('assets')


def supported_video_folder_path() -> pathlib.Path:
    return assets_folder_path().joinpath('videos').joinpath('supported')


def path_to_str(path: pathlib.Path):
    return str(path.resolve())
