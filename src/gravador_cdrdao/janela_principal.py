from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from gravador_cdrdao.dispositivos import DispositivoOptico
from gravador_cdrdao.requisitos import ResultadoRequisitos
from gravador_cdrdao.viewmodel_principal import ViewModelPrincipal


@dataclass
class EscolhaAssistente:
    mapeamento: dict[str, str]


class DialogoRequisitos(QtWidgets.QDialog):
    def __init__(self, resultado: ResultadoRequisitos, comandos: dict[str, str]) -> None:
        super().__init__()
        self.setWindowTitle("Requisitos não atendidos")
        self.setModal(True)
        layout = QtWidgets.QVBoxLayout(self)
        texto = QtWidgets.QLabel("Requisitos ausentes:")
        layout.addWidget(texto)
        lista = QtWidgets.QListWidget()
        for item in resultado.itens:
            if not item.presente:
                estado = "obrigatório" if item.obrigatorio else "opcional"
                lista.addItem(f"{item.nome} ({estado}) - {item.mensagem}")
        layout.addWidget(lista)
        comandos_label = QtWidgets.QLabel(
            "Comandos sugeridos:\n"
            f"Base: {comandos['base']}\n"
            f"Opcionais: {comandos['opcionais']}"
        )
        comandos_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(comandos_label)
        self.botao_copiar = QtWidgets.QPushButton("Copiar comandos")
        self.botao_fechar = QtWidgets.QPushButton("Continuar com recursos limitados")
        botoes = QtWidgets.QHBoxLayout()
        botoes.addWidget(self.botao_copiar)
        botoes.addWidget(self.botao_fechar)
        layout.addLayout(botoes)
        self.botao_copiar.clicked.connect(
            lambda: QtWidgets.QApplication.clipboard().setText(
                f"{comandos['base']}\n{comandos['opcionais']}"
            )
        )
        self.botao_fechar.clicked.connect(self.accept)


class DialogoAssistenteMismatch(QtWidgets.QDialog):
    def __init__(self, sugestoes: dict[str, list[str]], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Assistente de Mismatch de Arquivos")
        self.setModal(True)
        self._mapeamento: dict[str, str] = {}
        layout = QtWidgets.QVBoxLayout(self)
        info = QtWidgets.QLabel(
            "Selecione o arquivo correto para cada referência do CUE."
        )
        layout.addWidget(info)
        self._combos: dict[str, QtWidgets.QComboBox] = {}
        for nome, lista in sugestoes.items():
            linha = QtWidgets.QHBoxLayout()
            linha.addWidget(QtWidgets.QLabel(nome))
            combo = QtWidgets.QComboBox()
            combo.addItems(lista)
            linha.addWidget(combo)
            layout.addLayout(linha)
            self._combos[nome] = combo
        botoes = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def obter_mapeamento(self) -> dict[str, str]:
        for nome, combo in self._combos.items():
            self._mapeamento[nome] = combo.currentText()
        return self._mapeamento


class JanelaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, viewmodel: ViewModelPrincipal) -> None:
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Gravador CDRDAO")
        self.resize(900, 600)
        self._configurar_ui()
        self._conectar_sinais()
        self.viewmodel.checar_requisitos()
        self.viewmodel.atualizar_dispositivos()

    def _configurar_ui(self) -> None:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        dispositivo_layout = QtWidgets.QHBoxLayout()
        dispositivo_layout.addWidget(QtWidgets.QLabel("Dispositivo:"))
        self.combo_dispositivos = QtWidgets.QComboBox()
        dispositivo_layout.addWidget(self.combo_dispositivos)
        self.botao_atualizar = QtWidgets.QPushButton("Atualizar lista")
        dispositivo_layout.addWidget(self.botao_atualizar)
        layout.addLayout(dispositivo_layout)

        imagem_layout = QtWidgets.QHBoxLayout()
        imagem_layout.addWidget(QtWidgets.QLabel("Imagem CUE/TOC:"))
        self.campo_imagem = QtWidgets.QLineEdit()
        self.botao_arquivo = QtWidgets.QPushButton("Selecionar")
        imagem_layout.addWidget(self.campo_imagem)
        imagem_layout.addWidget(self.botao_arquivo)
        layout.addLayout(imagem_layout)

        opcoes_layout = QtWidgets.QHBoxLayout()
        self.check_simular = QtWidgets.QCheckBox("Simular antes de gravar")
        self.check_ps1 = QtWidgets.QCheckBox("Modo PS1 recomendado")
        self.spin_velocidade = QtWidgets.QSpinBox()
        self.spin_velocidade.setRange(1, 52)
        self.spin_velocidade.setValue(8)
        opcoes_layout.addWidget(self.check_simular)
        opcoes_layout.addWidget(self.check_ps1)
        opcoes_layout.addWidget(QtWidgets.QLabel("Velocidade:"))
        opcoes_layout.addWidget(self.spin_velocidade)
        layout.addLayout(opcoes_layout)

        botoes_layout = QtWidgets.QHBoxLayout()
        self.botao_validar = QtWidgets.QPushButton("Validar")
        self.botao_corrigir = QtWidgets.QPushButton("Corrigir")
        self.botao_simular = QtWidgets.QPushButton("Simular")
        self.botao_gravar = QtWidgets.QPushButton("Gravar")
        self.botao_cancelar = QtWidgets.QPushButton("Cancelar")
        self.botao_apagar = QtWidgets.QPushButton("Apagar CD-RW")
        botoes_layout.addWidget(self.botao_validar)
        botoes_layout.addWidget(self.botao_corrigir)
        botoes_layout.addWidget(self.botao_simular)
        botoes_layout.addWidget(self.botao_gravar)
        botoes_layout.addWidget(self.botao_apagar)
        botoes_layout.addWidget(self.botao_cancelar)
        layout.addLayout(botoes_layout)

        self.progress_label = QtWidgets.QLabel("Pronto.")
        layout.addWidget(self.progress_label)

        self.tabs = QtWidgets.QTabWidget()
        self.tab_logs = QtWidgets.QTextEdit()
        self.tab_logs.setReadOnly(True)
        self.tab_diagnostico = QtWidgets.QTextEdit()
        self.tab_diagnostico.setReadOnly(True)
        self.tab_info = QtWidgets.QTextEdit()
        self.tab_info.setReadOnly(True)
        self.tabs.addTab(self.tab_logs, "Logs")
        self.tabs.addTab(self.tab_diagnostico, "Diagnóstico")
        self.tabs.addTab(self.tab_info, "Info")
        layout.addWidget(self.tabs)

        self.setCentralWidget(widget)

    def _conectar_sinais(self) -> None:
        self.botao_atualizar.clicked.connect(self.viewmodel.atualizar_dispositivos)
        self.botao_arquivo.clicked.connect(self._selecionar_arquivo)
        self.botao_validar.clicked.connect(self._validar)
        self.botao_corrigir.clicked.connect(self._corrigir)
        self.botao_simular.clicked.connect(self._simular)
        self.botao_gravar.clicked.connect(self._gravar)
        self.botao_cancelar.clicked.connect(self.viewmodel.cancelar_operacao)
        self.botao_apagar.clicked.connect(self._apagar)
        self.combo_dispositivos.currentIndexChanged.connect(self._atualizar_info_drive)

        self.viewmodel.requisitos_atualizados.connect(self._mostrar_requisitos)
        self.viewmodel.dispositivos_atualizados.connect(self._atualizar_lista)
        self.viewmodel.log_atualizado.connect(self.tab_logs.setPlainText)
        self.viewmodel.diagnostico_atualizado.connect(self.tab_diagnostico.setPlainText)
        self.viewmodel.progresso_atualizado.connect(self.progress_label.setText)
        self.viewmodel.info_drive_atualizada.connect(self.tab_info.setPlainText)

    def _mostrar_requisitos(self, resultado: ResultadoRequisitos) -> None:
        if resultado.obrigatorios_pendentes():
            comandos = self.viewmodel.sugerir_comandos(resultado.distro)
            dialogo = DialogoRequisitos(resultado, comandos)
            dialogo.exec()

    def _atualizar_lista(self, dispositivos: list[DispositivoOptico]) -> None:
        self.combo_dispositivos.clear()
        for item in dispositivos:
            texto = f"{item.caminho} - {item.fabricante} {item.modelo}"
            self.combo_dispositivos.addItem(texto, item)
        if dispositivos:
            self._atualizar_info_drive()

    def _selecionar_arquivo(self) -> None:
        caminho, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Selecionar imagem CUE/TOC",
            str(Path.home()),
            "Imagens (*.cue *.toc)",
        )
        if caminho:
            self.campo_imagem.setText(caminho)

    def _validar(self) -> None:
        ok, msg = self.viewmodel.validar_cue(self.campo_imagem.text())
        QtWidgets.QMessageBox.information(self, "Validação", msg)
        if not ok:
            self._abrir_assistente_mismatch()

    def _corrigir(self) -> None:
        ok, msg = self.viewmodel.corrigir_cue(self.campo_imagem.text())
        QtWidgets.QMessageBox.information(self, "Correção", msg)

    def _abrir_assistente_mismatch(self) -> None:
        ok, msg, sugestoes = self.viewmodel.assistente_mismatch(
            self.campo_imagem.text()
        )
        if ok:
            return
        dialogo = DialogoAssistenteMismatch(sugestoes, self)
        if dialogo.exec() == QtWidgets.QDialog.Accepted:
            mapeamento = dialogo.obter_mapeamento()
            ok, msg = self.viewmodel.aplicar_mapeamento(
                self.campo_imagem.text(), mapeamento
            )
            QtWidgets.QMessageBox.information(self, "Assistente", msg)

    def _simular(self) -> None:
        dev = self._dispositivo_selecionado()
        cue = self.campo_imagem.text()
        self.viewmodel.iniciar_simulacao(dev, self.spin_velocidade.value(), cue)

    def _gravar(self) -> None:
        dev = self._dispositivo_selecionado()
        cue = self.campo_imagem.text()
        if self.check_ps1.isChecked():
            self.check_simular.setChecked(True)
            self.spin_velocidade.setValue(4)
        if self.check_simular.isChecked():
            self.viewmodel.iniciar_simulacao(dev, self.spin_velocidade.value(), cue)
        self.viewmodel.iniciar_gravacao(dev, self.spin_velocidade.value(), cue)

    def _apagar(self) -> None:
        dev = self._dispositivo_selecionado()
        self.viewmodel.iniciar_apagar(dev)

    def _dispositivo_selecionado(self) -> str:
        data = self.combo_dispositivos.currentData()
        if isinstance(data, DispositivoOptico):
            return data.caminho
        return "/dev/sr0"

    def _atualizar_info_drive(self) -> None:
        dev = self._dispositivo_selecionado()
        self.viewmodel.obter_info_drive(dev)
