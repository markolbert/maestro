import configuration
from processors import target_path, backupFile

@target_path("/etc/hostname")
def WriteHostname(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)

    file = open(fileInfo.targetPath, "w")
    file.write("{}\n".format(configInfo.local.name))
    file.close()
