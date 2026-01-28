from __future__ import annotations

import dataclasses
import re
from pathlib import Path
from typing import Iterable


@dataclasses.dataclass
class IndiceCue:
    numero: str
    tempo: str


@dataclasses.dataclass
class FaixaCue:
    numero: str
    tipo: str
    indices: list[IndiceCue]


@dataclasses.dataclass
class ArquivoCue:
    caminho: str
    tipo: str
    faixas: list[FaixaCue]


@dataclasses.dataclass
class CueSheet:
    arquivos: list[ArquivoCue]


_RE_FILE = re.compile(r'^FILE\s+"(?P<caminho>.+?)"\s+(?P<tipo>\S+)', re.I)
_RE_TRACK = re.compile(r'^TRACK\s+(?P<numero>\d{2})\s+(?P<tipo>\S+)', re.I)
_RE_INDEX = re.compile(r'^INDEX\s+(?P<numero>\d{2})\s+(?P<tempo>\d{2}:\d{2}:\d{2})', re.I)


def _normalizar_aspas(texto: str) -> str:
    return (
        texto.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
    )


def _remover_bom(texto: str) -> str:
    return texto.lstrip("\ufeff")


def _normalizar_finais_linha(texto: str) -> str:
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def corrigir_conteudo_cue(conteudo: str) -> str:
    return _normalizar_finais_linha(_remover_bom(_normalizar_aspas(conteudo)))


def carregar_cue(caminho: Path) -> CueSheet:
    conteudo = caminho.read_text(encoding="utf-8", errors="replace")
    conteudo = corrigir_conteudo_cue(conteudo)

    arquivos: list[ArquivoCue] = []
    arquivo_atual: ArquivoCue | None = None
    faixa_atual: FaixaCue | None = None

    for linha_bruta in conteudo.splitlines():
        linha = linha_bruta.strip()
        if not linha:
            continue
        if match := _RE_FILE.match(linha):
            arquivo_atual = ArquivoCue(
                caminho=match.group("caminho"),
                tipo=match.group("tipo"),
                faixas=[],
            )
            arquivos.append(arquivo_atual)
            faixa_atual = None
            continue
        if match := _RE_TRACK.match(linha):
            if arquivo_atual is None:
                raise ValueError("TRACK encontrado antes de FILE.")
            faixa_atual = FaixaCue(
                numero=match.group("numero"),
                tipo=match.group("tipo"),
                indices=[],
            )
            arquivo_atual.faixas.append(faixa_atual)
            continue
        if match := _RE_INDEX.match(linha):
            if faixa_atual is None:
                raise ValueError("INDEX encontrado antes de TRACK.")
            faixa_atual.indices.append(
                IndiceCue(numero=match.group("numero"), tempo=match.group("tempo"))
            )
            continue

    if not arquivos:
        raise ValueError("Nenhum arquivo FILE encontrado.")
    return CueSheet(arquivos=arquivos)


def resolver_caminhos_relativos(cue: CueSheet, base: Path) -> CueSheet:
    arquivos = []
    for arquivo in cue.arquivos:
        caminho = Path(arquivo.caminho)
        if not caminho.is_absolute():
            caminho = (base / caminho).resolve()
        arquivos.append(
            ArquivoCue(
                caminho=str(caminho),
                tipo=arquivo.tipo,
                faixas=arquivo.faixas,
            )
        )
    return CueSheet(arquivos=arquivos)


def listar_arquivos_cue(cue: CueSheet) -> list[str]:
    return [arquivo.caminho for arquivo in cue.arquivos]


def detectar_mismatch_nomes(cue: CueSheet, pasta: Path) -> dict[str, list[str]]:
    existentes = {p.name: p for p in pasta.iterdir() if p.is_file()}
    sugestoes: dict[str, list[str]] = {}
    for arquivo in cue.arquivos:
        nome = Path(arquivo.caminho).name
        if nome not in existentes:
            sugestoes[nome] = list(existentes.keys())
    return sugestoes


def aplicar_mapeamento_nomes(conteudo: str, mapeamento: dict[str, str]) -> str:
    novo = conteudo
    for antigo, novo_nome in mapeamento.items():
        novo = re.sub(rf'FILE\s+"{re.escape(antigo)}"', f'FILE "{novo_nome}"', novo)
    return novo


def validar_arquivos_existem(cue: CueSheet) -> list[str]:
    ausentes = []
    for arquivo in cue.arquivos:
        if not Path(arquivo.caminho).exists():
            ausentes.append(arquivo.caminho)
    return ausentes


def formatar_sumario(cue: CueSheet) -> str:
    linhas: list[str] = []
    for arquivo in cue.arquivos:
        linhas.append(f"Arquivo: {arquivo.caminho} ({arquivo.tipo})")
        for faixa in arquivo.faixas:
            linhas.append(f"  Track {faixa.numero} ({faixa.tipo})")
            for indice in faixa.indices:
                linhas.append(f"    Index {indice.numero} {indice.tempo}")
    return "\n".join(linhas)


def iterar_faixas(cue: CueSheet) -> Iterable[FaixaCue]:
    for arquivo in cue.arquivos:
        for faixa in arquivo.faixas:
            yield faixa
