from __future__ import annotations

import dataclasses
import re
from typing import Pattern


@dataclasses.dataclass
class DiagnosticoErro:
    titulo: str
    explicacao: str
    causa_provavel: str
    como_resolver: str
    acoes: list[str]


@dataclasses.dataclass
class RegraErro:
    nome: str
    padrao: Pattern[str]
    diagnostico: DiagnosticoErro


class ClassificadorErros:
    def __init__(self) -> None:
        self._regras: list[RegraErro] = [
            RegraErro(
                nome="permissao",
                padrao=re.compile(r"(permission denied|cannot open device)", re.I),
                diagnostico=DiagnosticoErro(
                    titulo="Permissão negada no dispositivo",
                    explicacao="O sistema bloqueou o acesso ao drive óptico.",
                    causa_provavel="Usuário fora do grupo correto ou ausência de polkit.",
                    como_resolver=(
                        "Adicione o usuário ao grupo cdrom/optical e faça logout/login."
                    ),
                    acoes=["Adicionar ao grupo", "Verificar polkit"],
                ),
            ),
            RegraErro(
                nome="arquivo_ausente",
                padrao=re.compile(r"(no such file|cannot open .*\.bin)", re.I),
                diagnostico=DiagnosticoErro(
                    titulo="Arquivos referenciados não encontrados",
                    explicacao="O CUE aponta para arquivos inexistentes.",
                    causa_provavel="Nome incorreto ou arquivo movido.",
                    como_resolver="Use o assistente de correção de nomes.",
                    acoes=["Abrir assistente"],
                ),
            ),
            RegraErro(
                nome="bom_crlf",
                padrao=re.compile(r"(illegal character|parse error)", re.I),
                diagnostico=DiagnosticoErro(
                    titulo="Formato do CUE inválido",
                    explicacao="O arquivo possui BOM, CRLF ou aspas inválidas.",
                    causa_provavel="Gerado em Windows ou editor antigo.",
                    como_resolver="Use a correção automática do CUE.",
                    acoes=["Corrigir automaticamente"],
                ),
            ),
            RegraErro(
                nome="velocidade",
                padrao=re.compile(r"(speed .* not allowed|illegal write speed)", re.I),
                diagnostico=DiagnosticoErro(
                    titulo="Velocidade incompatível",
                    explicacao="A mídia não suporta a velocidade informada.",
                    causa_provavel="Velocidade alta demais para o drive ou mídia.",
                    como_resolver="Reduza a velocidade e tente novamente.",
                    acoes=["Ajustar velocidade"],
                ),
            ),
            RegraErro(
                nome="usb_reset",
                padrao=re.compile(r"(resetting usb|usb disconnect)", re.I),
                diagnostico=DiagnosticoErro(
                    titulo="Instabilidade USB",
                    explicacao="O drive desconectou durante a gravação.",
                    causa_provavel="Autosuspend ou cabo/porta instável.",
                    como_resolver="Desative autosuspend temporariamente.",
                    acoes=["Desativar autosuspend"],
                ),
            ),
        ]

    def classificar(self, log: str) -> DiagnosticoErro | None:
        for regra in self._regras:
            if regra.padrao.search(log):
                return regra.diagnostico
        return None
