from __future__ import annotations

import os
import signal
import subprocess
import threading
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

CallbackSaida = Callable[[str], None]


@dataclass(frozen=True)
class ResultadoExecucao:
    codigo_retorno: int
    stdout: str
    stderr: str


class ExecutorComandos:
    def __init__(self) -> None:
        self._processo: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()

    def executar_com_stream(
        self,
        args: list[str],
        callback_stdout: Optional[CallbackSaida] = None,
        callback_stderr: Optional[CallbackSaida] = None,
        diretorio_trabalho: Optional[str] = None,
    ) -> ResultadoExecucao:
        stdout_buffer: list[str] = []
        stderr_buffer: list[str] = []

        def _ler_stream(stream: Iterable[str], callback: Optional[CallbackSaida], buffer: list[str]) -> None:
            for linha in stream:
                buffer.append(linha)
                if callback:
                    callback(linha)

        with self._lock:
            self._processo = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=diretorio_trabalho,
            )

        assert self._processo.stdout is not None
        assert self._processo.stderr is not None

        thread_stdout = threading.Thread(
            target=_ler_stream, args=(self._processo.stdout, callback_stdout, stdout_buffer), daemon=True
        )
        thread_stderr = threading.Thread(
            target=_ler_stream, args=(self._processo.stderr, callback_stderr, stderr_buffer), daemon=True
        )
        thread_stdout.start()
        thread_stderr.start()
        thread_stdout.join()
        thread_stderr.join()
        codigo_retorno = self._processo.wait()

        with self._lock:
            self._processo = None

        return ResultadoExecucao(codigo_retorno, "".join(stdout_buffer), "".join(stderr_buffer))

    def cancelar(self) -> None:
        with self._lock:
            if not self._processo:
                return
            try:
                self._processo.send_signal(signal.SIGINT)
                self._processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._processo.send_signal(signal.SIGTERM)

    def esta_em_execucao(self) -> bool:
        with self._lock:
            return self._processo is not None and self._processo.poll() is None

    def forcar_parada(self) -> None:
        with self._lock:
            if not self._processo:
                return
            try:
                os.kill(self._processo.pid, signal.SIGKILL)
            except OSError:
                return
