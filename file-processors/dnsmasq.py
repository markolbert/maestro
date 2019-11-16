import os
from getpass import getpass
import pexpect
import configuration
from processors import target_path, copyFile

@target_path("/etc/dnsmasq.d/localnet.conf")
def WriteConfigDnsmasq(configInfo: configuration.ConfigInfo, fileInfo: configuration.MaestroFile):
    # fileInfo gets replaced by the targeted entry from configInfo.files by the decorator
    replacements = [
        "# listen on the following interface(s)",
        "interface={}".format(configInfo.interface)
    ]

    if configInfo.local.isMaestro:
        replacements.append("interface={}".format(configInfo.tunnelInterface))

    copyFile(fileInfo.sourcePath, fileInfo.targetPath, { "@@interfaces@@" : replacements })

    path = "/var/lib/misc"
    if not os.path.exists(path):
        os.makedirs(path, mode=0o644, exist_ok=True)

    filePath = "{}/dnsmasq.leases".format(path)
    temp = getpass("Enter mark's password on the other system:")

    child = pexpect.spawn("scp mark@mycroft:{} {}".format(filePath, path))

    while True:
        lineNum = child.expect(["connecting (yes/no)?", "password:", pexpect.EOF], timeout=5)

        if lineNum == 0:
            child.sendline("yes")
        elif lineNum == 1:
            child.sendline(temp)
        elif lineNum == 2:
            print("Imported {}".format(filePath))
            break
        else:
            raise ValueError("Unexpected response")
