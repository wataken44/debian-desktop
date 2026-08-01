#!/usr/bin/env python

""" reset_network_connection.py


"""

import logging
import re
import subprocess
import sys
import time
import urllib.request

logger = logging.getLogger(__name__)

CONNECTION_TYPE_LOOPBACK = "loopback"
CONNECTION_TYPE_DICT = {"e": "802-3-ethernet", "wl": "802-11-wireless"}

CHECK_URL_LIST = [
    "http://deb.debian.org/",
    "https://www.debian.org/",
    "https://www.yahoo.co.jp/",
    "https://github.com/",
]
CHECK_INTERVAL = 30
CHECK_COUNT = 16


def main():
    configure_logger()

    delete_connection()
    add_connection_by_device()
    restart_network_manager()
    wait_for_network()


def configure_logger():
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        "/tmp/reset_network_connection.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


def delete_connection():
    # to avoid infinite loop, loop 64 times
    for _ in range(64):
        con_list = get_connection_list()

        delete_uuid_list = []
        for con in con_list:
            if (
                con.type != CONNECTION_TYPE_LOOPBACK
                and con.uuid not in delete_uuid_list
            ):
                delete_uuid_list.append(con.uuid)

        if len(delete_uuid_list) == 0:
            for uuid in delete_uuid_list:
                execute(["nmcli", "connection", "delete", "uuid", uuid])


def add_connection_by_device():
    iface_list = get_interface_list()

    for iface in iface_list:
        for k, v in CONNECTION_TYPE_DICT.items():
            if iface.name.startswith(k):
                execute(
                    [
                        "nmcli",
                        "connection",
                        "add",
                        "con-name",
                        iface.name,
                        "type",
                        v,
                        "ifname",
                        iface.name,
                    ]
                )
            break


def restart_network_manager():
    execute(["systemctl", "restart", "NetworkManager.service"])


def wait_for_network():
    for x in range(CHECK_COUNT):
        for url in CHECK_URL_LIST:
            logger.info("check connectivity to %s (%d/%d)" % (url, x + 1, CHECK_COUNT))
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Mozilla/5.0")

            try:
                _ = urllib.request.urlopen(req, timeout=10)
                logger.info("connected to %s" % url)
                return
            except Exception as e:
                logger.info(str(e))

        time.sleep(CHECK_INTERVAL)


def get_interface_list():
    ret = []

    proc = execute(["ip", "a"])
    name = None

    for line in proc.stdout.splitlines():
        # interface name
        mo = re.match(r"^\d+:\s+([^:@]+)", line)
        if mo:
            name = mo.group(1)
            continue

        # type and mac address
        mo = re.search(
            r"link/(\S+)\s+([0-9a-f:]{17})",
            line,
            re.IGNORECASE,
        )
        if mo and name:
            link_type = mo.group(1)
            mac = mo.group(2)
            ret.append(Interface(name, mac, link_type))

    return ret


def get_connection_list():
    ret = []
    proc = execute(["nmcli", "--terse", "connection", "show"])

    for line in proc.stdout.splitlines():
        arr = line.strip().split(":")
        if len(arr) != 4:
            continue

        ret.append(Connection(arr[0], arr[1], arr[2], arr[3]))

    return ret


def execute(args):
    shell = False
    if type(args) == str:
        shell = True

    logger.info(f"command: {str(args)}")

    proc = subprocess.run(args, shell=shell, capture_output=True, text=True)

    logger.info(
        f"rc: {proc.returncode}\nstdout: \n{proc.stdout}\nstderr: \n{proc.stderr}"
    )

    return proc


class Interface(object):
    def __init__(self, name, mac, type_):
        self._name = name
        self._mac = mac.lower()
        self._type = type_

    def __str__(self):
        return f"Interface({self.name}, {self.mac}, {self.type})"

    def to_dict(self):
        return {
            "name": self._name,
            "mac": self._mac,
            "type": self._type,
        }

    # properties

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    name = property(get_name, set_name, None, "")

    def get_mac(self):
        return self._mac

    def set_mac(self, mac):
        self._mac = mac

    mac = property(get_mac, set_mac, None, "")

    def get_type(self):
        return self._type

    def set_type(self, type_):
        self._type = type_

    type = property(get_type, set_type, None, "")


class Connection(object):
    def __init__(self, name, uuid, type_, device):
        self._name = name
        self._uuid = uuid
        self._type = type_
        self._device = device

    def __str__(self):
        return f"Connection({self.name}, {self.uuid}, {self.type}, {self.device})"

    def to_dict(self):
        return {
            "name": self._name,
            "uuid": self._uuid,
            "type": self._type,
            "device": self._device,
        }

    # properties

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    name = property(get_name, set_name, None, "")

    def get_uuid(self):
        return self._uuid

    def set_uuid(self, uuid):
        self._uuid = uuid

    uuid = property(get_uuid, set_uuid, None, "")

    def get_type(self):
        return self._type

    def set_type(self, type_):
        self._type = type_

    type = property(get_type, set_type, None, "")

    def get_device(self):
        return self._device

    def set_device(self, device):
        self._device = device

    device = property(get_device, set_device, None, "")


if __name__ == "__main__":
    main()
