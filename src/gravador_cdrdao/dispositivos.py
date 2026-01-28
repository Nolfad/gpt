from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class DispositivoOptico:
    caminho: str
    fabricante: str
    modelo: str
    sg: str | None


def _ler_modelo_sr(caminho: Path) -> tuple[str, str]:
    try:
        vendor = (caminho / "device/vendor").read_text().strip()
        model = (caminho / "device/model").read_text().strip()
        return vendor, model
    except Exception:
        return "Desconhecido", "Desconhecido"


def _mapear_sg(caminho: str) -> str | None:
    base = Path(caminho).name
    if not base.startswith("sr"):
        return None
    candidato = f"/dev/sg{base[2:]}"
    return candidato if os.path.exists(candidato) else None


def listar_dispositivos() -> list[DispositivoOptico]:
    dispositivos: list[DispositivoOptico] = []
    for caminho in sorted(Path("/sys/class/block").glob("sr*")):
        vendor, model = _ler_modelo_sr(caminho)
        dev = f"/dev/{caminho.name}"
        dispositivos.append(
            DispositivoOptico(
                caminho=dev,
                fabricante=vendor,
                modelo=model,
                sg=_mapear_sg(dev),
            )
        )
    return dispositivos


def obter_info_lsblk() -> dict[str, dict[str, str]]:
    if not shutil_disponivel():
        return {}
    try:
        proc = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,MODEL,VENDOR"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return {}
        dados = json.loads(proc.stdout)
    except Exception:
        return {}
    info: dict[str, dict[str, str]] = {}
    for item in dados.get("blockdevices", []):
        nome = item.get("name")
        if nome:
            info[f"/dev/{nome}"] = {
                "modelo": item.get("model") or "",
                "fabricante": item.get("vendor") or "",
            }
    return info


def shutil_disponivel() -> bool:
    return shutil.which("lsblk") is not None


def info_drive_cdrdao(dev: str) -> str:
    try:
        proc = subprocess.run(
            ["cdrdao", "inquiry", "--device", dev],
            check=False,
            capture_output=True,
            text=True,
        )
        return proc.stdout + proc.stderr
    except Exception as exc:
        return f"Falha ao obter info via cdrdao: {exc}"


def info_midia_cdrdao(dev: str) -> str:
    try:
        proc = subprocess.run(
            ["cdrdao", "disk-info", "--device", dev],
            check=False,
            capture_output=True,
            text=True,
        )
        return proc.stdout + proc.stderr
    except Exception as exc:
        return f"Falha ao obter info de mídia: {exc}"
