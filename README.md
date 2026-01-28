# Gravador CDRDAO

Aplicativo Linux com GUI (PySide6) focado em gravar CDs usando **cdrdao**, com ênfase em imagens CUE/BIN multi-trilha (PS1). O app mantém uma arquitetura MVVM, logs detalhados e um diagnóstico inteligente de erros.

## Requisitos

- Python 3.10+ (recomendado 3.12+)
- Qt/PySide6
- cdrdao instalado no sistema
- (Opcional) dvd+rw-tools para informações avançadas de mídia

## Executar (modo desenvolvimento)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Principais funcionalidades

- Detecção de dispositivos `/dev/sr*` e `/dev/sg*`.
- Validação de `.cue` com verificação de arquivos referenciados.
- Simulação e gravação usando `cdrdao`.
- Logs detalhados e painel de diagnóstico.
- Assistente de correções para CRLF/BOM e erros comuns.

## Empacotamento (.deb)

O pacote `.deb` pode ser gerado com `dpkg-buildpackage` ou ferramentas como `fpm`. Um exemplo mínimo:

```bash
fpm -s dir -t deb \
  --name gravador-cdrdao \
  --version 0.1.0 \
  --depends python3-pyside6 \
  --depends cdrdao \
  app/=/opt/gravador-cdrdao/
```

## Soluções rápidas

- **Permissão negada**: adicione o usuário ao grupo `cdrom` e reinicie a sessão.
- **CRLF/BOM no CUE**: use o corretor integrado para converter para LF e remover BOM.
- **Reset USB**: troque cabo/porta e desative autosuspend durante a gravação.
