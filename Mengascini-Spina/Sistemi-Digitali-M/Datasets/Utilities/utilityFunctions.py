from pathlib import Path

def get_files_with_type(folder:Path,extensions:tuple) ->list:
    """
    Given a filder and a lists of extensions, returns the paths of all the files in the folder with one of these extensions
    :param folder: path of the folder
    :param extensions: tuple of extensions (eg: ("*.jpg","*.tiff")
    :return:list of paths
    """
    files = []
    for extension in extensions:
        files.extend(folder.glob(extension))
    return files


def getExisting(files_list :list):
    """
    Given a list of filenames test if each of them exists returning a list of only existing files
    :param files_list: list of paths of the files
    :return: list of path of the existing files
    """
    existing_files = []

    for file in files_list:

        if not file.isFile():
            continue

        existing_files.append(file)

    return existing_files