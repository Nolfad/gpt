from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.dominio.corretor_cue import CorretorCue
from app.dominio.validador_imagem_cue import ValidadorImagemCue
from app.diagnostico.classificador_erros import DiagnosticoErro


@dataclass(frozen=True)
class AcaoCorrecao:
    codigo: str
    descricao: str
    requer_privilegio: bool


class AssistenteCorrecao:
    def __init__(self) -> None:
        self._corretor = CorretorCue()
        self._validador = ValidadorImagemCue()

    def propor_acoes(self, diagnostico: DiagnosticoErro) -> list[AcaoCorrecao]:
        if diagnostico.codigo_erro == "crlf_bom":
            return [
                AcaoCorrecao(codigo="corrigir_crlf", descricao="Converter CRLF para LF", requer_privilegio=False),
                AcaoCorrecao(codigo="remover_bom", descricao="Remover BOM do arquivo", requer_privilegio=False),
            ]
        if diagnostico.codigo_erro == "permissao":
            return [
                AcaoCorrecao(
                    codigo="adicionar_grupo_cdrom",
                    descricao="Adicionar usuário ao grupo cdrom",
                    requer_privilegio=True,
                )
            ]
        if diagnostico.codigo_erro == "arquivo_ausente":
            return [
                AcaoCorrecao(
                    codigo="ajustar_nomes",
                    descricao="Atualizar nomes de arquivos no .cue",
                    requer_privilegio=False,
                )
            ]
        if diagnostico.codigo_erro == "usb_reset":
            return [
                AcaoCorrecao(
                    codigo="desativar_autosuspend",
                    descricao="Desativar autosuspend USB durante a gravação",
                    requer_privilegio=True,
                )
            ]
        return []

    def aplicar_acao(self, acao: AcaoCorrecao, caminho_cue: Path) -> str:
        if acao.codigo == "corrigir_crlf":
            self._corretor.converter_crlf_para_lf(caminho_cue)
            return "CRLF convertido para LF."
        if acao.codigo == "remover_bom":
            self._corretor.remover_bom(caminho_cue)
            return "BOM removido."
        if acao.codigo == "ajustar_nomes":
            return "Assistente de ajuste de nomes deve ser executado via UI."
        if acao.codigo == "adicionar_grupo_cdrom":
            return "Ação requer helper com polkit."
        if acao.codigo == "desativar_autosuspend":
            return "Ação requer helper com polkit."
        return "Ação não reconhecida."

    def validar_novamente(self, caminho_cue: Path) -> str:
        resultado = self._validador.validar_cue(caminho_cue)
        if resultado.valido:
            return "Validação concluída sem erros críticos."
        return "Persistem problemas no arquivo .cue."
