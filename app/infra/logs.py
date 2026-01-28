from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

NOME_APP = "Gravador CDRDAO"
DIRETORIO_LOGS = Path.home() / ".local" / "share" / "gravador_cdrdao" / "logs"
QUANTIDADE_MAXIMA_LOGS = 10


@dataclass(frozen=True)
class ConfiguracaoLog:
    caminho_arquivo: Path
    logger: logging.Logger


def _limpar_logs_antigos() -> None:
    if not DIRETORIO_LOGS.exists():
        return
    arquivos = sorted(DIRETORIO_LOGS.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for arquivo in arquivos[QUANTIDADE_MAXIMA_LOGS:]:
        try:
            arquivo.unlink()
        except OSError:
            continue


def configurar_logging() -> ConfiguracaoLog:
    DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
    _limpar_logs_antigos()
    nome_arquivo = datetime.now().strftime("gravador_cdrdao_%Y%m%d_%H%M%S.log")
    caminho_arquivo = DIRETORIO_LOGS / nome_arquivo

    logger = logging.getLogger("gravador_cdrdao")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatacao = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler_arquivo = logging.FileHandler(caminho_arquivo, encoding="utf-8")
    handler_arquivo.setFormatter(formatacao)
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatacao)

    logger.addHandler(handler_arquivo)
    logger.addHandler(handler_console)

    return ConfiguracaoLog(caminho_arquivo=caminho_arquivo, logger=logger)
