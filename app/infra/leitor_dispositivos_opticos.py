from __future__ import annotations

import glob
import subprocess
from pathlib import Path
from typing import Iterable

from app.dominio.modelos import DetalhesDispositivo, DispositivoOptico


class LeitorDispositivosOpticos:
    def listar_dispositivos(self) -> list[DispositivoOptico]:
        dispositivos: list[DispositivoOptico] = []
        for caminho in sorted(glob.glob("/dev/sr*")):
            dispositivos.append(DispositivoOptico(caminho=caminho, tipo="sr"))
        for caminho in sorted(glob.glob("/dev/sg*")):
            dispositivos.append(DispositivoOptico(caminho=caminho, tipo="sg"))
        return dispositivos

    def _executar(self, args: list[str]) -> str:
        try:
            retorno = subprocess.run(args, capture_output=True, text=True, check=False)
            if retorno.returncode != 0:
                return ""
            return retorno.stdout.strip()
        except FileNotFoundError:
            return ""

    def obter_detalhes_dispositivo(self, dev: str) -> DetalhesDispositivo:
        fabricante = "Desconhecido"
        modelo = "Desconhecido"
        capacidades: list[str] = []
        saida = self._executar(["lsblk", "-no", "VENDOR,MODEL", dev])
        if saida:
            partes = saida.split(maxsplit=1)
            if partes:
                fabricante = partes[0]
                if len(partes) > 1:
                    modelo = partes[1]
        if Path(dev).exists():
            capacidades.append("Gravação")
        return DetalhesDispositivo(caminho=dev, fabricante=fabricante, modelo=modelo, tipo="optico", capacidades=capacidades)
