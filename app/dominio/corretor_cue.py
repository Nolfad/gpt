from __future__ import annotations

import codecs
from pathlib import Path


class CorretorCue:
    def converter_crlf_para_lf(self, caminho: Path) -> None:
        conteudo = caminho.read_text(encoding="utf-8", errors="replace")
        caminho.write_text(conteudo.replace("\r\n", "\n"), encoding="utf-8")

    def remover_bom(self, caminho: Path) -> None:
        dados = caminho.read_bytes()
        if dados.startswith(codecs.BOM_UTF8):
            caminho.write_bytes(dados[len(codecs.BOM_UTF8) :])

    def ajustar_nomes_file(self, caminho_cue: Path, mapeamento: dict[str, str]) -> None:
        conteudo = caminho_cue.read_text(encoding="utf-8", errors="replace")
        for antigo, novo in mapeamento.items():
            conteudo = conteudo.replace(f'FILE "{antigo}"', f'FILE "{novo}"')
        caminho_cue.write_text(conteudo, encoding="utf-8")
