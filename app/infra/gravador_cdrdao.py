from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from app.infra.executor_comandos import ExecutorComandos, ResultadoExecucao

CallbackSaida = Callable[[str], None]


@dataclass(frozen=True)
class ResultadoGravacao:
    execucao: ResultadoExecucao
    comando: list[str]


class GravadorCdrdao:
    def __init__(self, executor: ExecutorComandos) -> None:
        self._executor = executor

    def simular(
        self,
        dev: str,
        velocidade: Optional[int],
        caminho_cue: Path,
        callback_stdout: Optional[CallbackSaida] = None,
        callback_stderr: Optional[CallbackSaida] = None,
    ) -> ResultadoGravacao:
        comando = ["cdrdao", "simulate", "--device", dev]
        if velocidade:
            comando += ["--speed", str(velocidade)]
        comando.append(str(caminho_cue))
        execucao = self._executor.executar_com_stream(comando, callback_stdout, callback_stderr)
        return ResultadoGravacao(execucao=execucao, comando=comando)

    def gravar(
        self,
        dev: str,
        velocidade: Optional[int],
        caminho_cue: Path,
        ejetar: bool,
        callback_stdout: Optional[CallbackSaida] = None,
        callback_stderr: Optional[CallbackSaida] = None,
    ) -> ResultadoGravacao:
        comando = ["cdrdao", "write", "--device", dev]
        if velocidade:
            comando += ["--speed", str(velocidade)]
        if ejetar:
            comando.append("--eject")
        comando.append(str(caminho_cue))
        execucao = self._executor.executar_com_stream(comando, callback_stdout, callback_stderr)
        return ResultadoGravacao(execucao=execucao, comando=comando)

    def apagar_cdrw(self, dev: str) -> ResultadoGravacao:
        comando = ["cdrdao", "blank", "--device", dev]
        execucao = self._executor.executar_com_stream(comando)
        return ResultadoGravacao(execucao=execucao, comando=comando)

    def obter_info_midia(self, dev: str) -> ResultadoGravacao:
        comando = ["cdrdao", "disk-info", "--device", dev]
        execucao = self._executor.executar_com_stream(comando)
        return ResultadoGravacao(execucao=execucao, comando=comando)
