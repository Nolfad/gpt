# Gravador CDRDAO

Aplicativo GUI em PySide6 que usa **cdrdao** para gravar CDs (com foco em CUE/BIN multi-trilha de PS1).

## Requisitos
- Python 3.10+ (ideal 3.12)
- PySide6
- cdrdao
- (Opcional) dvd+rw-tools, lsblk, udevadm, pkexec/polkit

## Instalação por distro
### Ubuntu/Debian
```bash
sudo apt install cdrdao python3-pyside6 dvd+rw-tools util-linux udev policykit-1
```

### Fedora
```bash
sudo dnf install cdrdao python3-pyside6 dvd+rw-tools util-linux udev polkit
```

### Arch
```bash
sudo pacman -S cdrdao python-pyside6 dvd+rw-tools util-linux udev polkit
```

## Execução local (venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m gravador_cdrdao.main
```

## Build e instalação de pacotes
### .deb
```bash
sudo apt install debhelper dh-python
cd packaging/debian
./build-deb.sh
sudo dpkg -i ../dist/gravador-cdrdao_0.1.0_all.deb
```

### .rpm
```bash
sudo dnf install rpm-build
cd packaging/rpm
./build-rpm.sh
sudo dnf install ../dist/gravador-cdrdao-0.1.0-1.noarch.rpm
```

### Flatpak
```bash
sudo flatpak install flathub org.kde.Sdk//6.6 org.kde.Platform//6.6
cd packaging/flatpak
flatpak-builder --user --install --force-clean build-dir br.com.gravadorcdrdao.yml
```

### AppImage
```bash
cd packaging/appimage
./build-appimage.sh
```

### Arch PKGBUILD (bônus)
```bash
cd packaging/arch
makepkg -si
```

## Troubleshooting
- Se o app disser “Permissão negada no dispositivo”, adicione seu usuário ao grupo `cdrom` ou `optical` e faça logout/login.
- Se estiver em Flatpak, a gravação pode ser bloqueada pelo sandbox. Use .deb/.rpm/AppImage para acesso total ao drive.

## Estrutura do projeto
```
src/gravador_cdrdao/
  app.py
  classificador_erros.py
  dispositivos.py
  executor_cdrdao.py
  janela_principal.py
  main.py
  parser_cue.py
  privilegios.py
  requisitos.py
resources/
  gravador-cdrdao-helper
  br.com.gravadorcdrdao.policy
packaging/
  debian/
  rpm/
  flatpak/
  appimage/
  arch/
```
