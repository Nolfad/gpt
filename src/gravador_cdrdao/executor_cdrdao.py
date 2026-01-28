from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Callable

from PySide6 import QtCore


@dataclass
class ProgressoCdrdao:
    mensagem: str
    faixa: str | None
    buffer: str | None


class ExecutorCdrdao(QtCore.QThread):
    progresso = QtCore.Signal(ProgressoCdrdao)
    finalizado = QtCore.Signal(int, str)

    def __init__(self, comando: list[str]) -> None:
        super().__init__()
        self._comando = comando
        self._processo: subprocess.Popen[str] | None = None
        self._cancelado = False

    def run(self) -> None:
        try:
            self._processo = subprocess.Popen(
                self._comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            saida = []
            assert self._processo.stdout
            for linha in self._processo.stdout:
                saida.append(linha)
                self._emitir_progresso(linha)
                if self._cancelado:
                    break
            if self._cancelado and self._processo.poll() is None:
                self._processo.terminate()
            codigo = self._processo.wait() if self._processo else 1
            self.finalizado.emit(codigo, "".join(saida))
        except Exception as exc:
            self.finalizado.emit(1, f"Falha ao executar: {exc}")

    def cancelar(self) -> None:
        self._cancelado = True
        if self._processo and self._processo.poll() is None:
            self._processo.terminate()

    def _emitir_progresso(self, linha: str) -> None:
        faixa = None
        buffer = None
        if match := re.search(r"Writing track\s+(\d+)", linha, re.I):
            faixa = match.group(1)
        if match := re.search(r"buffer\s*([0-9]+%)", linha, re.I):
            buffer = match.group(1)
        mensagem = linha.strip()
        if mensagem:
            self.progresso.emit(ProgressoCdrdao(mensagem=mensagem, faixa=faixa, buffer=buffer))


class ExecutorCdrdaoFactory:
    @staticmethod
    def criar_simulacao(dev: str, velocidade: int, cue: str) -> ExecutorCdrdao:
        return ExecutorCdrdao(
            ["cdrdao", "simulate", "--device", dev, "--speed", str(velocidade), cue]
        )

    @staticmethod
    def criar_gravacao(dev: str, velocidade: int, cue: str) -> ExecutorCdrdao:
        return ExecutorCdrdao(
            [
                "cdrdao",
                "write",
                "--device",
                dev,
                "--speed",
                str(velocidade),
                "--eject",
                cue,
            ]
        )

    @staticmethod
    def criar_apagar(dev: str) -> ExecutorCdrdao:
        return ExecutorCdrdao(["cdrdao", "blank", "--device", dev])
