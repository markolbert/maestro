import os
import shutil
from typing import Dict
import functools
import configuration
import logging

def isFilePathValid(fileName, checkExist=True):
    """determines if a file path is valid and optionally checks to see if the file exists (which is the default)"""
    try:
        with open(fileName, 'x') as tempFile:
            return True
    except OSError:
        return checkExist and os.path.exists(fileName)


def ensureLineExists(fileInfo: configuration.MaestroFile, reqdLine: str):
    """ensures a specified line exists in a config file, adding it if necessary"""
    logger = logging.getLogger("maestro")

    file = open(fileInfo.targetPath, "r")
    matchedLines = [line for line in file if reqdLine in line]
    file.close()

    if not matchedLines:
        file = open(fileInfo.targetPath, "a")
        file.write("\n{}\n".format(reqdLine))
        file.close()

        logger.log(0, "added '{}' to {}".format(reqdLine, fileInfo.targetPath))
        return True
    else:
        logger.warning("{} already includes '{}'".format(fileInfo.targetPath, reqdLine))
        return False


def backupFile(fileInfo: configuration.MaestroFile, backupExt:str = ".backup"):
    """backs up a config file if it exists"""
    logger = logging.getLogger("maestro")

    if os.path.exists(fileInfo.targetPath):
        logger.log(0, "Backing up {}".format(fileInfo.targetPath))
        shutil.copyfile(fileInfo.targetPath, fileInfo.targetPath + backupExt)
    else:
        logger.warning("{} does not exist, not backed up".format(fileInfo.targetPath))


def copyFile(sourcePath: str, targetPath: str, replacements: Dict = {}):
    """copies a source file to a target file, replacing text elements if specified"""
    logger = logging.getLogger("maestro")

    if not isFilePathValid(sourcePath, True):
        logger.warning("couldn't copy {} to {}, source path is invalid or nonexistent".format(sourcePath, targetPath))
        return False

    if not isFilePathValid(targetPath):
        logger.warning("couldn't copy {} to {}, target path is invalid".format(sourcePath, targetPath))
        return False

    if replacements is None:
        shutil.copyfile(sourcePath, targetPath)
        logger.log(0, "copied {} to {}".format(sourcePath, targetPath))
        return True

    logger.log(0, "copying {} to {} and replacing lines".format(sourcePath, targetPath))

    file = open(sourcePath, "r")
    inputLines = file.readlines()
    file.close()

    outputLines = []

    for line in inputLines:
        replacementKey = next((x for x in replacements.keys() if "@@{}@@".format(x) == line), None)

        if replacementKey is None:
            outputLines.append(line)
        else:
            logger.log(0, "replaced lines tagged by {}".format(replacementKey))

            for newLine in replacements[replacementKey]:
                outputLines.append(newLine + "\n")

    file = open(targetPath, "w")
    file.writelines(outputLines)
    file.close()


def target_path(targetPath:str):
    """wraps a file processing function so that the file to be processed is specified as kind of metadata
    in the decorator"""
    logger = logging.getLogger("maestro")

    def decorator_target_path(func):
        @functools.wraps(func)
        def wrapper_target_path(*args, **kwargs):
            if len(args) != 2:
                logger.warning("target_path decorated function has {} arguments when 2 are expected".format(len(args)))
            elif isinstance(args[0], configuration.ConfigInfo):
                configInfo = args[0]
                fileInfo = next((x for x in configInfo.files if x.targetPath == targetPath), None)

                if fileInfo is None:
                    logger.warning("No configuration defined for {}".format(targetPath))
                else:
                    logger.log(0, "processing {}".format(targetPath))
                    newArgs = (args[0], fileInfo)
                    func(*newArgs, **kwargs)
            else:
                logger.warning("1st argument passed to target_path wrapped function is not a ConfigInfo")

            return targetPath
        return wrapper_target_path
    return decorator_target_path

