from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6 import QtCore

from app.diagnostico.classificador_erros import ClassificadorErros, ContextoErro, DiagnosticoErro
from app.dominio.modelos import ResultadoValidacao
from app.dominio.validador_imagem_cue import ValidadorImagemCue
from app.infra.executor_comandos import ExecutorComandos
from app.infra.gravador_cdrdao import GravadorCdrdao
from app.infra.leitor_dispositivos_opticos import LeitorDispositivosOpticos


@dataclass(frozen=True)
class ProgressoGravacao:
    percentual: int
    etapa: str
    buffer: Optional[str]


class MainViewModel(QtCore.QObject):
    dispositivos_atualizados = QtCore.Signal(list)
    detalhes_atualizados = QtCore.Signal(str)
    validacao_atualizada = QtCore.Signal(ResultadoValidacao)
    log_atualizado = QtCore.Signal(str)
    progresso_atualizado = QtCore.Signal(ProgressoGravacao)
    diagnostico_atualizado = QtCore.Signal(DiagnosticoErro)
    estado_botoes = QtCore.Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._leitor = LeitorDispositivosOpticos()
        self._validador = ValidadorImagemCue()
        self._executor = ExecutorComandos()
        self._gravador = GravadorCdrdao(self._executor)
        self._classificador = ClassificadorErros()
        self._caminho_cue: Optional[Path] = None
        self._dispositivo: Optional[str] = None

    def atualizar_dispositivos(self) -> None:
        dispositivos = self._leitor.listar_dispositivos()
        self.dispositivos_atualizados.emit(dispositivos)

    def selecionar_dispositivo(self, caminho: str) -> None:
        self._dispositivo = caminho
        detalhes = self._leitor.obter_detalhes_dispositivo(caminho)
        texto = f"{detalhes.fabricante} {detalhes.modelo}"
        self.detalhes_atualizados.emit(texto)

    def selecionar_cue(self, caminho: Path) -> None:
        self._caminho_cue = caminho
        resultado = self._validador.validar_cue(caminho)
        self.validacao_atualizada.emit(resultado)

    def _interpretar_progresso(self, linha: str) -> None:
        if "%" in linha:
            partes = linha.split("%")
            numero = "".join(filter(str.isdigit, partes[0]))
            if numero:
                percentual = min(100, max(0, int(numero)))
                etapa = linha.strip()
                self.progresso_atualizado.emit(ProgressoGravacao(percentual, etapa, None))

    def _callback_stdout(self, linha: str) -> None:
        self.log_atualizado.emit(linha)
        self._interpretar_progresso(linha)

    def _callback_stderr(self, linha: str) -> None:
        self.log_atualizado.emit(linha)
        self._interpretar_progresso(linha)

    def validar(self) -> None:
        if not self._caminho_cue:
            return
        resultado = self._validador.validar_cue(self._caminho_cue)
        self.validacao_atualizada.emit(resultado)

    def simular(self, velocidade: Optional[int]) -> None:
        if not self._dispositivo or not self._caminho_cue:
            return
        self.estado_botoes.emit(False)
        resultado = self._gravador.simular(
            self._dispositivo,
            velocidade,
            self._caminho_cue,
            callback_stdout=self._callback_stdout,
            callback_stderr=self._callback_stderr,
        )
        self._tratar_resultado_execucao(resultado.execucao.stdout, resultado.execucao.stderr, resultado.comando)
        self.estado_botoes.emit(True)

    def gravar(self, velocidade: Optional[int], ejetar: bool) -> None:
        if not self._dispositivo or not self._caminho_cue:
            return
        self.estado_botoes.emit(False)
        resultado = self._gravador.gravar(
            self._dispositivo,
            velocidade,
            self._caminho_cue,
            ejetar,
            callback_stdout=self._callback_stdout,
            callback_stderr=self._callback_stderr,
        )
        self._tratar_resultado_execucao(resultado.execucao.stdout, resultado.execucao.stderr, resultado.comando)
        self.estado_botoes.emit(True)

    def cancelar(self) -> None:
        self._executor.cancelar()

    def forcar_parada(self) -> None:
        self._executor.forcar_parada()

    def _tratar_resultado_execucao(self, stdout: str, stderr: str, comando: list[str]) -> None:
        diagnostico = self._classificador.classificar(
            stderr,
            stdout,
            ContextoErro(comando=comando, dispositivo=self._dispositivo, caminho_imagem=str(self._caminho_cue)),
        )
        if diagnostico:
            self.diagnostico_atualizado.emit(diagnostico)
