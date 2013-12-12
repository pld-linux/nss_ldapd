# TODO:
# - consider name change
#
Summary:	LDAP Name Service Switch Module
Summary(es.UTF-8):	Biblioteca NSS para LDAP
Summary(pl.UTF-8):	Moduł NSS LDAP
Summary(pt_BR.UTF-8):	Biblioteca NSS para LDAP
Name:		nss_ldapd
Version:	0.9.2
Release:	3
License:	LGPL v2.1+
Group:		Base
Source0:	http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz
# Source0-md5:	0c60d4c300dd9a4fb40b6ba7abeed8a2
Source1:	nslcd.init
Source2:	nslcd.service
Source3:	nslcd.tmpfiles
Patch0:		%{name}-no-root.patch
Patch1:		optimize-queries.patch
Patch2:		ntohl-signedness.patch
Patch3:		fix-to_date.patch
URL:		http://arthurdejong.org/nss-pam-ldapd/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	docbook2X
BuildRequires:	heimdal-devel
BuildRequires:	openldap-devel >= 2.3.0
BuildRequires:	pam-devel
BuildRequires:	rpmbuild(macros) >= 1.671
Requires:	nslcd = %{version}-%{release}
Conflicts:	nss_ldap
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		/%{_lib}

%description
nss_ldapd is a C library extension (NSS module) and daemon which
allows X.500 and LDAP directory servers to be used as a primary source
of aliases, ethers, groups, hosts, networks, protocols, users, RPCs,
services and shadow passwords (instead of or in addition to using flat
files or NIS).

%description -l pl.UTF-8
Moduł serwisu nazw oraz osobny demon. Ten pakiet pozwala na
korzystanie z serwerów X.500 i LDAP jako źródła aliasów, grup, hostów,
sieci, protokołów, użytkowników, RPC, usług i haseł (zamiast lub
oprócz zwykłych plików lub NIS).

nss_ldapd jest forkiem projektu nss_ldap. Celem projektu jest
naprawienie pewnych problemów z nss_ldap poprzez wydzielenie kodu LDAP
do osobnego demona.

%package nslcd
Summary:	NSS LDAPD name service daemon
Summary(pl.UTF-8):	Demon serwisu nazw NSS LDAPD
Group:		Base
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	rc-scripts >= 0.2.0
Requires:	systemd-units >= 38
Provides:	nslcd = %{version}-%{release}

%description nslcd
NSS LDAPD name service daemon.

%description nslcd -l pl.UTF-8
Demon serwisu nazw NSS LDAPD.

%package nslcd-utils
Summary:	Utilities using NSLCD for LDAPD operations
Summary(pl.UTF-8):	Demon serwisu nazw NSS LDAPD
Group:		Base
Requires:	nslcd = %{version}-%{release}

%description nslcd-utils
Utilities using NSLCD for LDAPD operations.

%description nslcd-utils -l pl.UTF-8
Narzędzia wykorzystujące NSLCD do operacji LDAP-owych.

%package pam
Summary:	NSS LDAPD Pluggable Authentication Module
Summary(pl.UTF-8):	Moduł PAM do uwierzytelniania z użyciem NSS LDAPD
Group:		Base
Requires:	nslcd = %{version}-%{release}
Conflicts:	pam-pam_ldap

%description pam
This is pam_ldap, a pluggable authentication module that can be used
with linux-PAM. This module supports authentication, account
management, password management and session management.

%description pam -l pl.UTF-8
To jest pam_ldap, wymienny moduł uwierzytelniania, który może być
użyty z linux-PAM. Moduł ten wspiera autentykację, obsługę kont,
zmianę haseł i obsługę sesji.

%prep
%setup -q -n nss-pam-ldapd-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%{__sed} -i -e '1s|#!.*|#!%{__python}|' utils/*.py

%build
%configure \
	DOCBOOK2X_MAN=/usr/bin/docbook2X2man \
	--with-pam-seclib-dir=/%{_lib}/security \
	--with-ldap-lib=openldap

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/rc.d/init.d,/var/run/nslcd} \
	$RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nslcd
install %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/nslcd.service
install %{SOURCE3} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/nslcd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%pre nslcd
%useradd -u 21 -d /usr/share/empty -s /bin/false -c "NSS LDAP Cache Daemon User" -g nobody nslcd

%post nslcd
/sbin/chkconfig --add nslcd
%service nslcd restart "NSS LDAP Cache Daemon"
%systemd_post nslcd.service

%preun nslcd
if [ "$1" = "0" ]; then
	%service nslcd stop
	/sbin/chkconfig --del nslcd
fi
%systemd_preun nslcd.service

%postun nslcd
if [ "$1" = "0" ]; then
	%userremove nslcd
fi
%systemd_reload

%triggerpostun nslcd -- nss_ldapd < 0.7.0
if [ -e %{_sysconfdir}/nss-ldapd.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/nslcd.conf{,rpmnew}
	mv -f %{_sysconfdir}/nss-ldapd.conf.rpmsave %{_sysconfdir}/nslcd.conf
fi

%triggerpostun nslcd -- nslcd < 0.9.2-1
%systemd_trigger nslcd.service

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%attr(755,root,root) %{_libdir}/libnss_ldap.so.2

%files nslcd
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/nslcd
%{systemdunitdir}/nslcd.service
%attr(640,nslcd,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nslcd.conf
%attr(755,root,root) %{_sbindir}/nslcd
%{_mandir}/man5/nslcd.conf.5*
%{_mandir}/man8/nslcd.8*
%dir /var/run/nslcd
%{systemdtmpfilesdir}/nslcd.conf

%files nslcd-utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/chsh.ldap
%attr(755,root,root) %{_bindir}/getent.ldap
%attr(755,root,root) %{_datadir}/nslcd-utils/chsh.py
%dir %{_datadir}/nslcd-utils
%{_datadir}/nslcd-utils/cmdline.py
%{_datadir}/nslcd-utils/constants.py
%attr(755,root,root) %{_datadir}/nslcd-utils/getent.py
%{_datadir}/nslcd-utils/nslcd.py
%{_datadir}/nslcd-utils/shells.py
%{_datadir}/nslcd-utils/users.py
%{_datadir}/nslcd-utils/*.py[co]
%{_mandir}/man1/chsh.ldap.1*
%{_mandir}/man1/getent.ldap.1*

%files pam
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_ldap.so
%{_mandir}/man8/pam_ldap.8*
