from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from app.diagnostico.classificador_erros import DiagnosticoErro
from app.dominio.modelos import DispositivoOptico, ResultadoValidacao
from app.viewmodels.main_viewmodel import MainViewModel, ProgressoGravacao


class JanelaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, viewmodel: MainViewModel) -> None:
        super().__init__()
        self._viewmodel = viewmodel
        self.setWindowTitle("Gravador CDRDAO")
        self.resize(900, 640)

        self._combo_dispositivos = QtWidgets.QComboBox()
        self._botao_atualizar = QtWidgets.QPushButton("Atualizar")
        self._label_detalhes = QtWidgets.QLabel("Fabricante/modelo")

        self._entrada_cue = QtWidgets.QLineEdit()
        self._botao_selecionar = QtWidgets.QPushButton("Selecionar")
        self._resumo_cue = QtWidgets.QLabel("Nenhuma imagem selecionada")

        self._spin_velocidade = QtWidgets.QSpinBox()
        self._spin_velocidade.setRange(1, 52)
        self._spin_velocidade.setValue(8)
        self._checkbox_auto = QtWidgets.QCheckBox("Auto")
        self._checkbox_auto.setChecked(True)
        self._checkbox_simular = QtWidgets.QCheckBox("Simular antes")
        self._checkbox_ejetar = QtWidgets.QCheckBox("Ejetar ao final")
        self._checkbox_conservador = QtWidgets.QCheckBox("Modo conservador (recomendado)")
        self._checkbox_ps1 = QtWidgets.QCheckBox("Perfil PS1 recomendado")

        self._botao_validar = QtWidgets.QPushButton("Validar")
        self._botao_corrigir = QtWidgets.QPushButton("Corrigir")
        self._botao_simular = QtWidgets.QPushButton("Simular")
        self._botao_gravar = QtWidgets.QPushButton("Gravar")
        self._botao_cancelar = QtWidgets.QPushButton("Cancelar")

        self._barra_progresso = QtWidgets.QProgressBar()
        self._texto_progresso = QtWidgets.QLabel("Aguardando ação")

        self._logs_texto = QtWidgets.QPlainTextEdit()
        self._logs_texto.setReadOnly(True)
        self._botao_copiar_logs = QtWidgets.QPushButton("Copiar")
        self._botao_salvar_logs = QtWidgets.QPushButton("Salvar")

        self._diagnostico_lista = QtWidgets.QListWidget()
        self._botao_aplicar_correcao = QtWidgets.QPushButton("Aplicar correção")

        self._montar_layout()
        self._conectar_sinais()
        self._viewmodel.atualizar_dispositivos()

    def _montar_layout(self) -> None:
        container = QtWidgets.QWidget()
        layout_principal = QtWidgets.QVBoxLayout(container)

        secao_dispositivo = QtWidgets.QGroupBox("Dispositivo")
        layout_dispositivo = QtWidgets.QGridLayout(secao_dispositivo)
        layout_dispositivo.addWidget(QtWidgets.QLabel("Gravador"), 0, 0)
        layout_dispositivo.addWidget(self._combo_dispositivos, 0, 1)
        layout_dispositivo.addWidget(self._botao_atualizar, 0, 2)
        layout_dispositivo.addWidget(self._label_detalhes, 1, 1, 1, 2)

        secao_imagem = QtWidgets.QGroupBox("Imagem")
        layout_imagem = QtWidgets.QGridLayout(secao_imagem)
        layout_imagem.addWidget(QtWidgets.QLabel("Arquivo"), 0, 0)
        layout_imagem.addWidget(self._entrada_cue, 0, 1)
        layout_imagem.addWidget(self._botao_selecionar, 0, 2)
        layout_imagem.addWidget(self._resumo_cue, 1, 1, 1, 2)

        secao_config = QtWidgets.QGroupBox("Configurações")
        layout_config = QtWidgets.QGridLayout(secao_config)
        layout_config.addWidget(QtWidgets.QLabel("Velocidade"), 0, 0)
        layout_config.addWidget(self._spin_velocidade, 0, 1)
        layout_config.addWidget(self._checkbox_auto, 0, 2)
        layout_config.addWidget(self._checkbox_simular, 1, 0)
        layout_config.addWidget(self._checkbox_ejetar, 1, 1)
        layout_config.addWidget(self._checkbox_conservador, 2, 0, 1, 2)
        layout_config.addWidget(self._checkbox_ps1, 2, 2)

        layout_botoes = QtWidgets.QHBoxLayout()
        for botao in [
            self._botao_validar,
            self._botao_corrigir,
            self._botao_simular,
            self._botao_gravar,
            self._botao_cancelar,
        ]:
            layout_botoes.addWidget(botao)

        area_progresso = QtWidgets.QVBoxLayout()
        area_progresso.addWidget(self._barra_progresso)
        area_progresso.addWidget(self._texto_progresso)

        abas = QtWidgets.QTabWidget()
        aba_logs = QtWidgets.QWidget()
        layout_logs = QtWidgets.QVBoxLayout(aba_logs)
        layout_logs.addWidget(self._logs_texto)
        layout_logs_botoes = QtWidgets.QHBoxLayout()
        layout_logs_botoes.addWidget(self._botao_copiar_logs)
        layout_logs_botoes.addWidget(self._botao_salvar_logs)
        layout_logs.addLayout(layout_logs_botoes)

        aba_diagnostico = QtWidgets.QWidget()
        layout_diag = QtWidgets.QVBoxLayout(aba_diagnostico)
        layout_diag.addWidget(self._diagnostico_lista)
        layout_diag.addWidget(self._botao_aplicar_correcao)

        abas.addTab(aba_logs, "Logs")
        abas.addTab(aba_diagnostico, "Diagnóstico")

        layout_principal.addWidget(secao_dispositivo)
        layout_principal.addWidget(secao_imagem)
        layout_principal.addWidget(secao_config)
        layout_principal.addLayout(layout_botoes)
        layout_principal.addLayout(area_progresso)
        layout_principal.addWidget(abas)

        self.setCentralWidget(container)

    def _conectar_sinais(self) -> None:
        self._botao_atualizar.clicked.connect(self._viewmodel.atualizar_dispositivos)
        self._combo_dispositivos.currentTextChanged.connect(self._viewmodel.selecionar_dispositivo)
        self._botao_selecionar.clicked.connect(self._selecionar_cue)
        self._botao_validar.clicked.connect(self._viewmodel.validar)
        self._botao_simular.clicked.connect(self._simular)
        self._botao_gravar.clicked.connect(self._gravar)
        self._botao_cancelar.clicked.connect(self._viewmodel.cancelar)
        self._botao_copiar_logs.clicked.connect(self._copiar_logs)

        self._viewmodel.dispositivos_atualizados.connect(self._preencher_dispositivos)
        self._viewmodel.detalhes_atualizados.connect(self._label_detalhes.setText)
        self._viewmodel.validacao_atualizada.connect(self._atualizar_validacao)
        self._viewmodel.log_atualizado.connect(self._adicionar_log)
        self._viewmodel.progresso_atualizado.connect(self._atualizar_progresso)
        self._viewmodel.diagnostico_atualizado.connect(self._exibir_diagnostico)
        self._viewmodel.estado_botoes.connect(self._alternar_botoes)

    def _preencher_dispositivos(self, dispositivos: list[DispositivoOptico]) -> None:
        self._combo_dispositivos.blockSignals(True)
        self._combo_dispositivos.clear()
        for dispositivo in dispositivos:
            self._combo_dispositivos.addItem(dispositivo.caminho)
        self._combo_dispositivos.blockSignals(False)
        if dispositivos:
            self._viewmodel.selecionar_dispositivo(dispositivos[0].caminho)

    def _selecionar_cue(self) -> None:
        caminho, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecionar CUE/TOC", "", "Cue/TOC (*.cue *.toc)")
        if caminho:
            self._entrada_cue.setText(caminho)
            self._viewmodel.selecionar_cue(Path(caminho))

    def _simular(self) -> None:
        velocidade = None if self._checkbox_auto.isChecked() else self._spin_velocidade.value()
        self._viewmodel.simular(velocidade)

    def _gravar(self) -> None:
        velocidade = None if self._checkbox_auto.isChecked() else self._spin_velocidade.value()
        self._viewmodel.gravar(velocidade, self._checkbox_ejetar.isChecked())

    def _atualizar_validacao(self, resultado: ResultadoValidacao) -> None:
        resumo = " | ".join(resultado.mensagens) if resultado.mensagens else "Arquivo válido"
        if resultado.faixas:
            resumo = f"Faixas: {len(resultado.faixas)}. {resumo}"
        self._resumo_cue.setText(resumo)

    def _adicionar_log(self, linha: str) -> None:
        self._logs_texto.appendPlainText(linha.rstrip())

    def _atualizar_progresso(self, progresso: ProgressoGravacao) -> None:
        self._barra_progresso.setValue(progresso.percentual)
        self._texto_progresso.setText(progresso.etapa)

    def _exibir_diagnostico(self, diagnostico: DiagnosticoErro) -> None:
        self._diagnostico_lista.clear()
        self._diagnostico_lista.addItem(diagnostico.mensagem_usuario)
        for causa in diagnostico.causas_provaveis:
            self._diagnostico_lista.addItem(f"Causa provável: {causa}")
        for acao in diagnostico.acoes_sugeridas:
            self._diagnostico_lista.addItem(f"Ação sugerida: {acao}")

    def _alternar_botoes(self, habilitado: bool) -> None:
        for botao in [self._botao_validar, self._botao_simular, self._botao_gravar, self._botao_corrigir]:
            botao.setEnabled(habilitado)

    def _copiar_logs(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self._logs_texto.toPlainText())

    def closeEvent(self, event: QtCore.QEvent) -> None:  # noqa: N802
        self._viewmodel.forcar_parada()
        super().closeEvent(event)
