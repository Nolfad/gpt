from __future__ import annotations

from pathlib import Path

from app.dominio.corretor_cue import CorretorCue


def test_corretor_converte_crlf(tmp_path: Path) -> None:
    cue = tmp_path / "teste.cue"
    cue.write_text("FILE \"a.bin\" BINARY\r\nTRACK 01 AUDIO\r\n", encoding="utf-8")

    CorretorCue().converter_crlf_para_lf(cue)

    assert "\r\n" not in cue.read_text(encoding="utf-8")


def test_corretor_remove_bom(tmp_path: Path) -> None:
    cue = tmp_path / "teste.cue"
    cue.write_bytes(b"\xef\xbb\xbfFILE \"a.bin\" BINARY\n")

    CorretorCue().remover_bom(cue)

    assert not cue.read_bytes().startswith(b"\xef\xbb\xbf")
