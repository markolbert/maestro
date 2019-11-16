import json
import dacite
import shutil
import pystemd
import socket
import pkgutil
import importlib
import inspect
import os
import subprocess
import configuration
import argparse
import logging

def matchesFunctionSignature(func, reqdParams: [] = []):
    """determines if an object is a function with a specific set of parameters"""
    if not inspect.isfunction(func):
        return False

    signature = inspect.signature(func)
    if len(signature.parameters) != len(reqdParams):
        return False

    for paramName in signature.parameters:
        idx = list(signature.parameters.keys()).index(paramName)
        if signature.parameters[paramName].annotation != reqdParams[idx]:
            return False

    return True


logger = logging.getLogger("maestro")

parser = argparse.ArgumentParser(description="parse maestro.py command line arguments")

parser.add_argument("-v", "--verbose", action="store_true", help="run in verbose mode")
parser.add_argument("-c", "--config", action="store", help="config file path", default="maestro.json")
parser.add_argument("-s", "--simulate", action="store_true", help="run in simulate mode, don't change anything")

cmdArgs = parser.parse_args()

if cmdArgs.verbose:
    logger.setLevel(logging.NOTSET)
else:
    logger.setLevel(logging.WARN)

if not os.path.exists(cmdArgs.config):
    logger.critical("config file {} does not exist".format(cmdArgs.config))
    exit(1)

# parse the configuration file and convert the resulting dictionary to defined classes
logger.info("parsing config file {}".format(cmdArgs.config))

configFile = open(cmdArgs.config, "r")
jsonDict = json.load(configFile)
jsonConfig = dacite.from_dict(data_class=configuration.MaestroConfig, data=jsonDict, config=dacite.Config(
    type_hooks={configuration.ServiceState: configuration.textToServiceState}))
configFile.close()

# check that we're running on a valid system
logger.log(0, "checking that we're running on a valid host")
hostName = socket.gethostname()

if hostName != jsonConfig.maestroName and hostName != jsonConfig.otherName:
    logger.critical("This program must be run on {} or {}".format(jsonConfig.maestroName, jsonConfig.otherName))
    exit(1)

# check that required apps exist
logger.log(0, "checking that required apps are available")
okay = True
for app in jsonConfig.apps:
    if shutil.which(app) is None:
        okay = False
        logger.critical("Couldn't find app {}".format(app))

if not okay:
    exit(1)

# check that required services exist
logger.log(0, "checking that required services exist")
okay = True
for svc in jsonConfig.services:
    if pystemd.systemd1.Unit(svc.name) is None:
        okay = False
        logger.critical("{} service is not installed".format(svc.name))

if not okay:
    exit(1)

# check mail server info
logger.log(0, "checking mail server information")
if jsonConfig.mail is None or jsonConfig.mail.serverName is None or jsonConfig.mail.userID is None:
    logger.critical("mail server information is invalid")
    exit(1)

# determine the necessary configuration for the machine on which we're running
config = configuration.ConfigInfo(jsonConfig)

# the required parameters for all file processing methods
reqdParams = [configuration.ConfigInfo, configuration.MaestroFile]
fileProcessors = []

# load all the modules in the file-processors folder
logging.log(0, "scanning file-processors folder for file processors")
fpModules = [name for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__) + "/file-processors"])]

# scan the modules for all functions matching that of a file processor
# (i.e., func(configuration.ConfigInfo, configuration.MaestroFile)
for modName in fpModules:
    imported = importlib.import_module('.' + modName, package='file-processors')

    for item in [x for x in dir(imported) if not x.startswith("__")]:
        attribute = getattr(imported, item)

        if matchesFunctionSignature(attribute, reqdParams):
            fileProcessors.append(attribute)

# grab the names of the files we're supposed to create/modify
filesToProcess = [x.targetPath for x in config.files]

# run each file processor against configuration.ConfigInfo (the MaestroFile second parameter will
# be set by the @target_path decorator so pass None for it here)
logging.info(0, "running file processors")
for fp in fileProcessors:
    logging.log(0, "running {}".format(fp.__name__))
    fileProcessed = fp(config, None)

    # file processors are supposed to return a string naming the file they
    # created/modified. if we don't get a string, or it's not in the list of
    # files to be processed, something went wrong
    if isinstance(fileProcessed, str) and fileProcessed in filesToProcess:
        logging.log(0, "processed {}".format(fileProcessed))
        filesToProcess.remove(fileProcessed)
    else:
        logging.warning("anomalous return from file processor {}".format(fp))

if len(filesToProcess) == 0:
    logging.log(0, "All configuration files processed")
else:
    logging.warning("The following files in maestro.json were not processed:")
    for missed in filesToProcess:
        logging.warning(missed)

logging.info("configuring services")
for svc in config.services:
    if svc.enabled == configuration.ServiceState.Always or config.local.isMaestro:
        logging.log(0, "starting and enabling {}".format(svc.name))
        subprocess.run(["systemctl", "start", svc.name])
        subprocess.run(["systemctl", "enable", svc.name])
    elif svc.enabled == configuration.ServiceState.OnlyAsMaestro and not config.local.isMaestro:
        logging.log(0, "stopping and disabling {}".format(svc.name))
        subprocess.run(["systemctl", "stop", svc.name])
        subprocess.run(["systemctl", "disable", svc.name])
