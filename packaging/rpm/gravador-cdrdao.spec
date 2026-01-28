Name:           gravador-cdrdao
Version:        0.1.0
Release:        1%{?dist}
Summary:        Gravador simples de CDs usando cdrdao
License:        GPL-3.0-or-later
URL:            https://example.com/gravador-cdrdao
BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3-pyside6 cdrdao polkit

%description
Aplicativo GUI com suporte a CUE/BIN multi-trilha (PS1).

%prep
%setup -q

%build
%py3_build

%install
%py3_install
install -D -m 0644 resources/gravador-cdrdao.desktop %{buildroot}%{_datadir}/applications/gravador-cdrdao.desktop
install -D -m 0644 resources/gravador-cdrdao.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/gravador-cdrdao.svg
install -D -m 0755 resources/gravador-cdrdao-helper %{buildroot}%{_libexecdir}/gravador-cdrdao-helper
install -D -m 0644 resources/br.com.gravadorcdrdao.policy %{buildroot}%{_datadir}/polkit-1/actions/br.com.gravadorcdrdao.policy

%files
%license README.md
%{python3_sitelib}/gravador_cdrdao*
%{_bindir}/gravador-cdrdao
%{_datadir}/applications/gravador-cdrdao.desktop
%{_datadir}/icons/hicolor/scalable/apps/gravador-cdrdao.svg
%{_libexecdir}/gravador-cdrdao-helper
%{_datadir}/polkit-1/actions/br.com.gravadorcdrdao.policy

%changelog
* Thu Jan 01 2024 Equipe Gravador CDRDAO <dev@example.com> - 0.1.0-1
- Versão inicial
