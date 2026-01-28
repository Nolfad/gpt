from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResultadoAcao:
    sucesso: bool
    mensagem: str


def executar_pkexec(acao: str, parametros: list[str]) -> ResultadoAcao:
    comando = ["pkexec", "gravador-cdrdao-helper", acao, *parametros]
    try:
        proc = subprocess.run(comando, check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            return ResultadoAcao(False, proc.stderr.strip() or proc.stdout.strip())
        return ResultadoAcao(True, proc.stdout.strip())
    except FileNotFoundError:
        return ResultadoAcao(False, "pkexec não encontrado.")
    except Exception as exc:
        return ResultadoAcao(False, f"Falha ao executar pkexec: {exc}")


def usuario_no_grupo(grupo: str) -> bool:
    try:
        proc = subprocess.run(["id", "-nG"], check=False, capture_output=True, text=True)
        return grupo in proc.stdout.split()
    except Exception:
        return False


def grupos_opticos() -> list[str]:
    return ["cdrom", "optical", "cdrw"]


def detectar_grupo_optico() -> str | None:
    for grupo in grupos_opticos():
        if Path(f"/etc/group").read_text(encoding="utf-8", errors="ignore").find(
            f"{grupo}:"
        ) != -1:
            return grupo
    return None
