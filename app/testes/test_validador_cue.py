from __future__ import annotations

from pathlib import Path

from app.dominio.validador_imagem_cue import ValidadorImagemCue


def test_validador_detecta_file_track(tmp_path: Path) -> None:
    cue = tmp_path / "jogo.cue"
    binario = tmp_path / "jogo.bin"
    binario.write_bytes(b"0" * 2_000_000)
    cue.write_text('FILE "jogo.bin" BINARY\nTRACK 01 MODE2/2352\nINDEX 01 00:00:00\n')

    resultado = ValidadorImagemCue().validar_cue(cue)

    assert resultado.valido is True
    assert len(resultado.arquivos) == 1
    assert len(resultado.faixas) == 1


def test_validador_detecta_crlf_e_bom(tmp_path: Path) -> None:
    cue = tmp_path / "jogo.cue"
    binario = tmp_path / "jogo.bin"
    binario.write_bytes(b"0" * 2_000_000)
    conteudo = b"\xef\xbb\xbfFILE \"jogo.bin\" BINARY\r\nTRACK 01 MODE2/2352\r\nINDEX 01 00:00:00\r\n"
    cue.write_bytes(conteudo)

    resultado = ValidadorImagemCue().validar_cue(cue)

    assert any("BOM" in mensagem for mensagem in resultado.mensagens)
    assert any("CRLF" in mensagem for mensagem in resultado.mensagens)
