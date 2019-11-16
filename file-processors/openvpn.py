import configuration
from processors import target_path, backupFile, ensureLineExists, copyFile

@target_path("/etc/openvpn/server.conf")
def WriteOpenVPN(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)
    ensureLineExists(fileInfo, 'config "/etc/openvpn/server-local.conf"')


@target_path("/etc/openvpn/server-local.conf")
def WriteOpenVPNLocal(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)
    copyFile(fileInfo.sourcePath, fileInfo.targetPath)
