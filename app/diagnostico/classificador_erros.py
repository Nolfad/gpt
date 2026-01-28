from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DiagnosticoErro:
    codigo_erro: str
    severidade: str
    mensagem_usuario: str
    causas_provaveis: list[str]
    acoes_sugeridas: list[str]
    pode_corrigir: bool


@dataclass(frozen=True)
class ContextoErro:
    comando: list[str]
    dispositivo: Optional[str] = None
    caminho_imagem: Optional[str] = None


class ClassificadorErros:
    def __init__(self) -> None:
        self._padroes = [
            (
                re.compile(
                    r"(Permission denied|Operation not permitted|cannot open device|Não é permitido|sem permissão|cannot open /dev/sr\d+)",
                    re.IGNORECASE,
                ),
                DiagnosticoErro(
                    codigo_erro="permissao",
                    severidade="erro",
                    mensagem_usuario="Sem permissão para acessar o gravador",
                    causas_provaveis=[
                        "Usuário não pertence ao grupo cdrom",
                        "Permissões do dispositivo estão restritas",
                    ],
                    acoes_sugeridas=[
                        "Adicionar usuário ao grupo cdrom",
                        "Sair e entrar novamente na sessão",
                        "Aplicar regra udev (com permissão)",
                    ],
                    pode_corrigir=True,
                ),
            ),
            (
                re.compile(
                    r'(Cannot open (data|audio) file|No such file or directory).*"(?P<arquivo>.*\.(bin|raw|wav))"',
                    re.IGNORECASE,
                ),
                DiagnosticoErro(
                    codigo_erro="arquivo_ausente",
                    severidade="erro",
                    mensagem_usuario="Arquivo referenciado no CUE não encontrado",
                    causas_provaveis=["Arquivo com nome diferente", "Arquivo está em outro diretório"],
                    acoes_sugeridas=["Abrir assistente para corrigir nomes", "Editar .cue automaticamente"],
                    pode_corrigir=True,
                ),
            ),
            (
                re.compile(r"(with CRLF line terminators|BOM)", re.IGNORECASE),
                DiagnosticoErro(
                    codigo_erro="crlf_bom",
                    severidade="alerta",
                    mensagem_usuario="O arquivo CUE possui formatação incompatível",
                    causas_provaveis=["Quebras CRLF", "BOM no início do arquivo"],
                    acoes_sugeridas=["Converter CRLF para LF", "Remover BOM"],
                    pode_corrigir=True,
                ),
            ),
            (
                re.compile(r"(reset (high-speed|SuperSpeed) USB device|USB disconnect|I/O error)", re.IGNORECASE),
                DiagnosticoErro(
                    codigo_erro="usb_reset",
                    severidade="erro",
                    mensagem_usuario="Instabilidade USB detectada durante a gravação",
                    causas_provaveis=["Cabo USB instável", "Porta USB com mau contato"],
                    acoes_sugeridas=[
                        "Trocar cabo ou porta USB",
                        "Desativar autosuspend durante a gravação",
                    ],
                    pode_corrigir=True,
                ),
            ),
            (
                re.compile(r"(speed .* not supported|falling back to|cannot set speed)", re.IGNORECASE),
                DiagnosticoErro(
                    codigo_erro="velocidade",
                    severidade="alerta",
                    mensagem_usuario="Velocidade solicitada não suportada",
                    causas_provaveis=["Velocidade acima do limite do drive"],
                    acoes_sugeridas=["Ativar modo conservador", "Reduzir velocidade"],
                    pode_corrigir=False,
                ),
            ),
        ]

    def classificar(self, stderr: str, stdout: str, contexto: ContextoErro) -> Optional[DiagnosticoErro]:
        texto = f"{stdout}\n{stderr}"
        for padrao, diagnostico in self._padroes:
            if padrao.search(texto):
                return diagnostico
        return None
