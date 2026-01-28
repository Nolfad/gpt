from __future__ import annotations

import sys

from PySide6 import QtWidgets

from app.infra.logs import configurar_logging
from app.ui.janela_principal import JanelaPrincipal
from app.viewmodels.main_viewmodel import MainViewModel


def main() -> int:
    configuracao = configurar_logging()
    configuracao.logger.info("Iniciando Gravador CDRDAO")
    app = QtWidgets.QApplication(sys.argv)
    viewmodel = MainViewModel()
    janela = JanelaPrincipal(viewmodel)
    janela.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
