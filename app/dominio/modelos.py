from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DispositivoOptico:
    caminho: str
    tipo: str


@dataclass(frozen=True)
class DetalhesDispositivo:
    caminho: str
    fabricante: str
    modelo: str
    tipo: str
    capacidades: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FaixaCue:
    numero: int
    tipo: str
    indice: Optional[str]


@dataclass(frozen=True)
class ArquivoCue:
    caminho: Path
    tipo: str


@dataclass(frozen=True)
class ResultadoValidacao:
    valido: bool
    mensagens: list[str]
    arquivos: list[ArquivoCue] = field(default_factory=list)
    faixas: list[FaixaCue] = field(default_factory=list)
    suspeito: bool = False
