import configuration
from processors import target_path, backupFile, ensureLineExists

@target_path("/etc/dhcpcd.conf")
def WriteDHCPCD(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)
    ensureLineExists(fileInfo, 'include "/etc/dhcpcd-interfaces.conf"')


@target_path("/etc/dhcpcd-interface.conf")
def WriteDHCPCDInterface(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    backupFile(fileInfo)

    file = open(fileInfo.targetPath, "w")

    file.write("interface {}\n".format(configInfo.interface))
    file.write("\tstatic ip_address={}/24\n".format(configInfo.local.ip))
    file.write("\tstatic routers={}\n".format(configInfo.gatewayIP))

    file.close()
