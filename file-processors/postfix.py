import subprocess
from getpass import getpass
import configuration
from processors import target_path, backupFile, copyFile


@target_path("/etc/postfix/header_check")
def WritePostfixHeaderCheck(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)
    copyFile(fileInfo.sourcePath, fileInfo.targetPath)
    subprocess.run(["postmap", fileInfo.targetPath])


@target_path("/etc/postfix/sasl_passwd")
def WritePostfixSaslPasswd(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)

    temp = getpass("Enter password for {} on {}:".format(configInfo.mail.userID, configInfo.mail.serverName))

    file = open(fileInfo.targetPath, "w")
    file.write("[{}]:{} {}:{}\n".format(configInfo.mail.serverName, configInfo.mail.serverPort,
                                        configInfo.mail.userID, temp))
    file.close()

    subprocess.run(["postmap", fileInfo.targetPath])


@target_path("/etc/postfix/sender_canonical_maps")
def WritePostfixSenderCanonicalMaps(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)
    copyFile(fileInfo.sourcePath, fileInfo.targetPath)
    subprocess.run(["postmap", fileInfo.targetPath])
