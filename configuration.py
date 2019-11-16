import fcntl
import struct
import enum
from dataclasses import dataclass
import socket
from typing import List, Optional
from arpreq import arpreq
import logging

class ServiceState(enum.Enum):
    """enum describing when a MaestroService should be enabled and running"""
    Always = 'always'
    OnlyAsMaestro = 'maestro'


def textToServiceState(text: str):
    """converts case-insensitive text to ServiceState enum (anything other than 'always' returns OnlyAsMaestro"""
    if str.lower(text) == 'always':
        return ServiceState.Always
    else:
        return ServiceState.OnlyAsMaestro


@dataclass
class MaestroFile:
    """describes a configuration file and an optional source path from which it should be created"""
    targetPath: str
    sourcePath: Optional[str]


@dataclass
class MaestroService:
    """describes a service and under what conditions it should be running/enabled"""
    name: str
    enabled: ServiceState


@dataclass
class MailServer:
    """describes the postfix email configuration"""
    serverName: str
    serverPort: int
    userID: str


@dataclass
class MaestroConfig:
    """the basic configuration information for maestro.py"""
    isMaestro: bool
    maestroIP: str
    otherIP: str
    gatewayIP: str
    maestroName: str
    otherName: str
    interface: str
    tunnelInterface: str
    mail: MailServer
    files: List[MaestroFile]
    services: List[MaestroService]
    apps: List[str]


class MachineInfo:
    """describes basic identity and networking information for a machine/host"""
    isMaestro: bool
    name: str
    ip: str
    mac: str


class ConfigInfo:
    """the configuration information for the local machine and the other machine of a configuration pair"""
    local: MachineInfo
    other: MachineInfo
    interface: str
    tunnelInterface: str
    gatewayIP: str
    mail: MailServer
    files: List[MaestroFile]
    services: List[MaestroService]

    def __init__(self, jsonConfig:MaestroConfig):
        logger = logging.getLogger("maestro")

        self.interface = jsonConfig.interface
        self.tunnelInterface = jsonConfig.tunnelInterface
        self.gatewayIP = jsonConfig.gatewayIP
        self.mail = jsonConfig.mail
        self.files = jsonConfig.files
        self.services = jsonConfig.services

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(jsonConfig.interface, 'utf-8')[:15]))
        localMac = ':'.join('%02x' % b for b in info[18:24])

        otherMac = arpreq(socket.gethostbyname(jsonConfig.otherName))
        if otherMac is None:
            logger.critical("Could not get MAC address for {}".format(jsonConfig.otherName))
            exit(1)

        self.local = MachineInfo()
        self.other = MachineInfo()

        if jsonConfig.isMaestro:
            self.local.isMaestro = True
            self.local.name = jsonConfig.maestroName
            self.local.ip = jsonConfig.maestroIP
            self.local.mac = localMac

            self.other.isMaestro = False
            self.other.name = jsonConfig.otherName
            self.other.ip = jsonConfig.otherIP
            self.other.mac = otherMac
        else:
            self.local.isMaestro = False
            self.local.name = jsonConfig.otherName
            self.local.ip = jsonConfig.otherIP
            self.local.mac = otherMac

            self.other.isMaestro = True
            self.other.name = jsonConfig.maestroName
            self.other.ip = jsonConfig.maestroIP
            self.other.mac = localMac

