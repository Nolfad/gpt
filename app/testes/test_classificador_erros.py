from __future__ import annotations

from app.diagnostico.classificador_erros import ClassificadorErros, ContextoErro


def test_classificador_detecta_permissao() -> None:
    classificador = ClassificadorErros()
    diagnostico = classificador.classificar(
        stderr="Permission denied ao abrir /dev/sr0",
        stdout="",
        contexto=ContextoErro(comando=["cdrdao"]),
    )
    assert diagnostico is not None
    assert diagnostico.codigo_erro == "permissao"


def test_classificador_detecta_arquivo_ausente() -> None:
    classificador = ClassificadorErros()
    diagnostico = classificador.classificar(
        stderr='Cannot open data file "jogo.bin"',
        stdout="",
        contexto=ContextoErro(comando=["cdrdao"]),
    )
    assert diagnostico is not None
    assert diagnostico.codigo_erro == "arquivo_ausente"
