from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def _adicionar_grupo_cdrom(usuario: str) -> int:
    return subprocess.call(["usermod", "-aG", "cdrom", usuario])


def _ajustar_autosuspend(caminho_sysfs: str, valor: str) -> int:
    try:
        caminho = Path(caminho_sysfs) / "power" / "control"
        caminho.write_text(valor, encoding="utf-8")
        return 0
    except OSError:
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Helper privilegiado do Gravador CDRDAO")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    grupo_parser = subparsers.add_parser("adicionar_grupo_cdrom")
    grupo_parser.add_argument("usuario")

    autosuspend_parser = subparsers.add_parser("autosuspend")
    autosuspend_parser.add_argument("caminho_sysfs")
    autosuspend_parser.add_argument("valor")

    args = parser.parse_args()

    if args.comando == "adicionar_grupo_cdrom":
        return _adicionar_grupo_cdrom(args.usuario)
    if args.comando == "autosuspend":
        return _ajustar_autosuspend(args.caminho_sysfs, args.valor)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
