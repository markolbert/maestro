import configuration
from processors import target_path, backupFile

@target_path("/etc/ethers")
def WriteEthers(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)

    file = open(fileInfo.targetPath, "a")
    file.write("{}\t{}.localnet\n".format(configInfo.local.mac, configInfo.local.name))
    file.write("{}\t{}.localnet\n".format(configInfo.other.mac, configInfo.other.name))
    file.close()
