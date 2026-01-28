from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path

from PySide6 import QtCore

from gravador_cdrdao.classificador_erros import ClassificadorErros
from gravador_cdrdao.dispositivos import DispositivoOptico, info_drive_cdrdao, info_midia_cdrdao, listar_dispositivos
from gravador_cdrdao.executor_cdrdao import ExecutorCdrdao, ExecutorCdrdaoFactory, ProgressoCdrdao
from gravador_cdrdao.parser_cue import (
    aplicar_mapeamento_nomes,
    carregar_cue,
    corrigir_conteudo_cue,
    detectar_mismatch_nomes,
    formatar_sumario,
    resolver_caminhos_relativos,
    validar_arquivos_existem,
)
from gravador_cdrdao.privilegios import detectar_grupo_optico, executar_pkexec, usuario_no_grupo
from gravador_cdrdao.requisitos import ResultadoRequisitos, checar_requisitos, comandos_por_distro


@dataclass
class EstadoOperacao:
    em_andamento: bool = False
    ultimo_log: str = ""
    diagnostico: str = ""


class ViewModelPrincipal(QtCore.QObject):
    requisitos_atualizados = QtCore.Signal(ResultadoRequisitos)
    dispositivos_atualizados = QtCore.Signal(list)
    log_atualizado = QtCore.Signal(str)
    diagnostico_atualizado = QtCore.Signal(str)
    progresso_atualizado = QtCore.Signal(str)
    info_drive_atualizada = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._classificador = ClassificadorErros()
        self._executor: ExecutorCdrdao | None = None
        self.estado = EstadoOperacao()

    def checar_requisitos(self) -> None:
        resultado = checar_requisitos()
        self.requisitos_atualizados.emit(resultado)

    def sugerir_comandos(self, distro: str) -> dict[str, str]:
        return comandos_por_distro(distro)

    def atualizar_dispositivos(self) -> None:
        dispositivos = listar_dispositivos()
        self.dispositivos_atualizados.emit(dispositivos)

    def validar_cue(self, caminho: str) -> tuple[bool, str]:
        try:
            cue = carregar_cue(Path(caminho))
            cue = resolver_caminhos_relativos(cue, Path(caminho).parent)
            ausentes = validar_arquivos_existem(cue)
            if ausentes:
                return False, "Arquivos ausentes: " + ", ".join(ausentes)
            return True, formatar_sumario(cue)
        except Exception as exc:
            return False, f"Falha ao validar: {exc}"

    def corrigir_cue(self, caminho: str) -> tuple[bool, str]:
        try:
            conteudo = Path(caminho).read_text(encoding="utf-8", errors="replace")
            corrigido = corrigir_conteudo_cue(conteudo)
            Path(caminho).write_text(corrigido, encoding="utf-8")
            return True, "Arquivo CUE corrigido com sucesso."
        except Exception as exc:
            return False, f"Falha ao corrigir: {exc}"

    def assistente_mismatch(self, caminho: str) -> tuple[bool, str, dict[str, list[str]]]:
        try:
            cue = carregar_cue(Path(caminho))
            sugestoes = detectar_mismatch_nomes(cue, Path(caminho).parent)
            if not sugestoes:
                return True, "Nenhum mismatch encontrado.", {}
            return False, "Mismatch de arquivos detectado.", sugestoes
        except Exception as exc:
            return False, f"Falha no assistente: {exc}", {}

    def aplicar_mapeamento(self, caminho: str, mapeamento: dict[str, str]) -> tuple[bool, str]:
        try:
            conteudo = Path(caminho).read_text(encoding="utf-8", errors="replace")
            novo = aplicar_mapeamento_nomes(conteudo, mapeamento)
            Path(caminho).write_text(novo, encoding="utf-8")
            return True, "CUE atualizado com novos nomes."
        except Exception as exc:
            return False, f"Falha ao aplicar mapeamento: {exc}"

    def iniciar_simulacao(self, dev: str, velocidade: int, cue: str) -> None:
        self._iniciar_executor(ExecutorCdrdaoFactory.criar_simulacao(dev, velocidade, cue))

    def iniciar_gravacao(self, dev: str, velocidade: int, cue: str) -> None:
        self._iniciar_executor(ExecutorCdrdaoFactory.criar_gravacao(dev, velocidade, cue))

    def iniciar_apagar(self, dev: str) -> None:
        self._iniciar_executor(ExecutorCdrdaoFactory.criar_apagar(dev))

    def cancelar_operacao(self) -> None:
        if self._executor:
            self._executor.cancelar()
            self.progresso_atualizado.emit("Cancelando operação...")

    def _iniciar_executor(self, executor: ExecutorCdrdao) -> None:
        if self._executor:
            self._executor.cancelar()
        self._executor = executor
        executor.progresso.connect(self._ao_progresso)
        executor.finalizado.connect(self._ao_finalizado)
        executor.start()

    def _ao_progresso(self, progresso: ProgressoCdrdao) -> None:
        mensagem = progresso.mensagem
        if progresso.faixa:
            mensagem = f"Escrevendo track {progresso.faixa} - {mensagem}"
        if progresso.buffer:
            mensagem = f"{mensagem} (Buffer {progresso.buffer})"
        self.progresso_atualizado.emit(mensagem)
        self._append_log(mensagem)

    def _ao_finalizado(self, codigo: int, log: str) -> None:
        self._append_log("Operação finalizada." if codigo == 0 else "Operação falhou.")
        self._append_log(log)
        diagnostico = self._classificador.classificar(log)
        if diagnostico:
            texto = (
                f"{diagnostico.titulo}\n{diagnostico.explicacao}\n"
                f"Causa provável: {diagnostico.causa_provavel}\n"
                f"Como resolver: {diagnostico.como_resolver}\n"
                f"Ações: {', '.join(diagnostico.acoes)}"
            )
            self.diagnostico_atualizado.emit(texto)

    def _append_log(self, texto: str) -> None:
        self.estado.ultimo_log += texto + "\n"
        self.log_atualizado.emit(self.estado.ultimo_log)

    def gerar_relatorio(self, dev: str, cue: str, comando: str, log: str) -> str:
        return (
            f"Sistema: {platform.platform()}\n"
            f"Kernel: {platform.release()}\n"
            f"Dispositivo: {dev}\n"
            f"Imagem: {cue}\n"
            f"Comando: {comando}\n"
            f"Log final:\n{log}\n"
        )

    def obter_info_drive(self, dev: str) -> None:
        info = info_drive_cdrdao(dev) + "\n" + info_midia_cdrdao(dev)
        self.info_drive_atualizada.emit(info)

    def verificar_grupo(self) -> tuple[bool, str | None]:
        grupo = detectar_grupo_optico()
        if not grupo:
            return False, None
        return usuario_no_grupo(grupo), grupo

    def adicionar_grupo(self, grupo: str) -> tuple[bool, str]:
        usuario = os.environ.get("USER", "")
        resultado = executar_pkexec("adicionar_grupo", [grupo, usuario])
        return resultado.sucesso, resultado.mensagem

    def definir_autosuspend(self, caminho: str, estado: str) -> tuple[bool, str]:
        resultado = executar_pkexec("autosuspend", [caminho, estado])
        return resultado.sucesso, resultado.mensagem
