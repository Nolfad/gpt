from __future__ import annotations

import codecs
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.dominio.modelos import ArquivoCue, FaixaCue, ResultadoValidacao

PADRAO_FILE = re.compile(r'^FILE\s+"(?P<caminho>.+)"\s+(?P<tipo>\w+)$', re.IGNORECASE)
PADRAO_TRACK = re.compile(r'^TRACK\s+(?P<numero>\d{2})\s+(?P<tipo>\w+)', re.IGNORECASE)
PADRAO_INDEX = re.compile(r'^INDEX\s+(?P<indice>\d{2})\s+(?P<tempo>\d{2}:\d{2}:\d{2})', re.IGNORECASE)


@dataclass(frozen=True)
class ResultadoLeituraCue:
    linhas: list[str]
    possui_bom: bool
    possui_crlf: bool


class ValidadorImagemCue:
    def _ler_cue(self, caminho: Path) -> ResultadoLeituraCue:
        dados = caminho.read_bytes()
        possui_bom = dados.startswith(codecs.BOM_UTF8)
        texto = dados.decode("utf-8", errors="replace")
        possui_crlf = "\r\n" in texto
        linhas = texto.splitlines()
        return ResultadoLeituraCue(linhas=linhas, possui_bom=possui_bom, possui_crlf=possui_crlf)

    def parsear_linhas_file_track_index(self, linhas: Iterable[str]) -> tuple[list[ArquivoCue], list[FaixaCue]]:
        arquivos: list[ArquivoCue] = []
        faixas: list[FaixaCue] = []
        arquivo_atual: Path | None = None

        for linha in linhas:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            combinacao_file = PADRAO_FILE.match(linha_limpa)
            if combinacao_file:
                caminho = Path(combinacao_file.group("caminho"))
                tipo = combinacao_file.group("tipo").upper()
                arquivos.append(ArquivoCue(caminho=caminho, tipo=tipo))
                arquivo_atual = caminho
                continue
            combinacao_track = PADRAO_TRACK.match(linha_limpa)
            if combinacao_track:
                numero = int(combinacao_track.group("numero"))
                tipo = combinacao_track.group("tipo").upper()
                faixas.append(FaixaCue(numero=numero, tipo=tipo, indice=None))
                continue
            combinacao_index = PADRAO_INDEX.match(linha_limpa)
            if combinacao_index and faixas:
                indice = combinacao_index.group("indice")
                faixa = faixas[-1]
                faixas[-1] = FaixaCue(numero=faixa.numero, tipo=faixa.tipo, indice=indice)

        return arquivos, faixas

    def validar_cue(self, caminho_cue: Path) -> ResultadoValidacao:
        mensagens: list[str] = []
        arquivos: list[ArquivoCue] = []
        faixas: list[FaixaCue] = []
        suspeito = False

        if not caminho_cue.exists():
            return ResultadoValidacao(False, ["Arquivo .cue não encontrado."])

        leitura = self._ler_cue(caminho_cue)
        if leitura.possui_bom:
            mensagens.append("O arquivo .cue possui BOM; isso pode causar erros no cdrdao.")
        if leitura.possui_crlf:
            mensagens.append("O arquivo .cue possui quebras de linha CRLF; recomenda-se converter para LF.")

        arquivos, faixas = self.parsear_linhas_file_track_index(leitura.linhas)
        if not arquivos:
            mensagens.append("Nenhuma linha FILE encontrada no .cue.")
        if not faixas:
            mensagens.append("Nenhuma linha TRACK encontrada no .cue.")

        for arquivo in arquivos:
            caminho = arquivo.caminho
            if not caminho.is_absolute():
                caminho = caminho_cue.parent / caminho
            if not caminho.exists():
                mensagens.append(f"Arquivo referenciado não encontrado: {arquivo.caminho}")
            else:
                tamanho = caminho.stat().st_size
                if tamanho < 1_000_000:
                    mensagens.append(
                        f"Arquivo {arquivo.caminho} parece pequeno ({tamanho} bytes). Verifique se a imagem está correta."
                    )
                    suspeito = True

        valido = len([m for m in mensagens if "não encontrado" in m.lower()]) == 0
        return ResultadoValidacao(valido, mensagens, arquivos=arquivos, faixas=faixas, suspeito=suspeito)
