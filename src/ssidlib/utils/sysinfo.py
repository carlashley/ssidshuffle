import subprocess

from dataclasses import dataclass, field


@dataclass
class OSVersion:
    version: str = field(default=None)
    build: str = field(default=None)
    major: str = field(default=None)
    minor: str = field(default=None)
    patch: str = field(default=None)
    name: str = field(default=None)
    rsr_version: int | str = field(default=None)


def _sw_vers():  # -> OSVersion:
    """Software Version."""
    vers_attrs_map = {"productname": "name",
                      "productversion": "version",
                      "buildversion": "build",
                      "productversionextra": "rsr_version"}
    cmd = ["/usr/bin/sw_vers"]
    p = subprocess.run(cmd, capture_output=True, encoding="utf-8")

    if p.returncode == 0:
        vers = {"rsr_version": None}

        for ln in p.stdout.strip().splitlines():
            key, val = [x.strip() for x in ln.split(":")]
            vers[vers_attrs_map[key.lower()]] = val

        sv = vers["version"].split(".")
        vers["major"] = int(sv[0])
        vers["minor"] = int(sv[1])

        try:
            vers["patch"] = int(sv[2])
        except IndexError:
            vers["patch"] = None

        return OSVersion(**vers)


def major_os_version() -> int:
    """Return the major OS version."""
    return _sw_vers().major
