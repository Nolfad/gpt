from __future__ import annotations

import os
import platform
import importlib.util
import shutil
import sys
from dataclasses import dataclass


@dataclass
class ItemRequisito:
    nome: str
    obrigatorio: bool
    presente: bool
    mensagem: str


@dataclass
class ResultadoRequisitos:
    itens: list[ItemRequisito]
    distro: str

    def obrigatorios_pendentes(self) -> list[ItemRequisito]:
        return [item for item in self.itens if item.obrigatorio and not item.presente]

    def opcionais_pendentes(self) -> list[ItemRequisito]:
        return [item for item in self.itens if not item.obrigatorio and not item.presente]


def _detectar_distro() -> str:
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().lower()
        if "fedora" in conteudo or "rhel" in conteudo or "centos" in conteudo:
            return "fedora"
        if "arch" in conteudo or "manjaro" in conteudo or "endeavouros" in conteudo:
            return "arch"
    return "debian"


def _tem_binario(nome: str) -> bool:
    return shutil.which(nome) is not None


def _tem_pyside6() -> bool:
    return importlib.util.find_spec("PySide6") is not None


def checar_requisitos() -> ResultadoRequisitos:
    distro = _detectar_distro()
    itens = [
        ItemRequisito(
            nome="Python 3.10+",
            obrigatorio=True,
            presente=sys.version_info >= (3, 10),
            mensagem=f"Versão atual: {platform.python_version()}",
        ),
        ItemRequisito(
            nome="PySide6",
            obrigatorio=True,
            presente=_tem_pyside6(),
            mensagem="Biblioteca de interface Qt.",
        ),
        ItemRequisito(
            nome="cdrdao",
            obrigatorio=True,
            presente=_tem_binario("cdrdao"),
            mensagem="Motor principal de gravação.",
        ),
        ItemRequisito(
            nome="dvd+rw-mediainfo",
            obrigatorio=False,
            presente=_tem_binario("dvd+rw-mediainfo"),
            mensagem="Informações extras da mídia.",
        ),
        ItemRequisito(
            nome="lsblk",
            obrigatorio=False,
            presente=_tem_binario("lsblk"),
            mensagem="Inventário de dispositivos.",
        ),
        ItemRequisito(
            nome="udevadm",
            obrigatorio=False,
            presente=_tem_binario("udevadm"),
            mensagem="Informações detalhadas de dispositivos.",
        ),
        ItemRequisito(
            nome="pkexec",
            obrigatorio=False,
            presente=_tem_binario("pkexec"),
            mensagem="Elevação de privilégios via PolicyKit.",
        ),
    ]
    return ResultadoRequisitos(itens=itens, distro=distro)


def comandos_por_distro(distro: str) -> dict[str, str]:
    if distro == "fedora":
        return {
            "base": "sudo dnf install cdrdao pyside6",
            "opcionais": "sudo dnf install dvd+rw-tools util-linux udev",
        }
    if distro == "arch":
        return {
            "base": "sudo pacman -S cdrdao python-pyside6",
            "opcionais": "sudo pacman -S dvd+rw-tools util-linux udev",
        }
    return {
        "base": "sudo apt install cdrdao python3-pyside6",
        "opcionais": "sudo apt install dvd+rw-tools util-linux udev",
    }
