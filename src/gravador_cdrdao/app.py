from __future__ import annotations

from PySide6 import QtWidgets

from gravador_cdrdao.janela_principal import JanelaPrincipal
from gravador_cdrdao.viewmodel_principal import ViewModelPrincipal


def criar_app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication([])


def iniciar() -> int:
    app = criar_app()
    viewmodel = ViewModelPrincipal()
    janela = JanelaPrincipal(viewmodel)
    janela.show()
    return app.exec()
