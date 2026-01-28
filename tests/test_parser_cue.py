from pathlib import Path

from gravador_cdrdao.classificador_erros import ClassificadorErros
from gravador_cdrdao.parser_cue import (
    aplicar_mapeamento_nomes,
    carregar_cue,
    corrigir_conteudo_cue,
    detectar_mismatch_nomes,
)


def test_corrigir_conteudo_remove_bom_e_crlf():
    texto = "\ufeffFILE \"teste.bin\" BINARY\r\nTRACK 01 AUDIO\r\n"
    corrigido = corrigir_conteudo_cue(texto)
    assert "\ufeff" not in corrigido
    assert "\r" not in corrigido


def test_carregar_cue_multi_arquivo(tmp_path: Path):
    cue = tmp_path / "disco.cue"
    cue.write_text(
        "FILE \"faixa1.bin\" BINARY\n"
        "TRACK 01 MODE1/2352\n"
        "INDEX 01 00:00:00\n"
        "FILE \"faixa2.bin\" BINARY\n"
        "TRACK 02 AUDIO\n"
        "INDEX 00 00:00:00\n"
        "INDEX 01 00:02:00\n",
        encoding="utf-8",
    )
    sheet = carregar_cue(cue)
    assert len(sheet.arquivos) == 2
    assert sheet.arquivos[0].faixas[0].numero == "01"


def test_detectar_mismatch(tmp_path: Path):
    cue = tmp_path / "disco.cue"
    cue.write_text(
        "FILE \"faixa_inexistente.bin\" BINARY\nTRACK 01 AUDIO\nINDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    (tmp_path / "faixa_real.bin").write_text("ok", encoding="utf-8")
    sheet = carregar_cue(cue)
    sugestoes = detectar_mismatch_nomes(sheet, tmp_path)
    assert "faixa_inexistente.bin" in sugestoes


def test_aplicar_mapeamento():
    conteudo = "FILE \"a.bin\" BINARY"
    novo = aplicar_mapeamento_nomes(conteudo, {"a.bin": "b.bin"})
    assert "b.bin" in novo


def test_classificador_erros():
    classificador = ClassificadorErros()
    diag = classificador.classificar("cannot open device")
    assert diag is not None
