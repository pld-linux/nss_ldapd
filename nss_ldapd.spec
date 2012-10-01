# TODO:
# - consider name change
#
Summary:	LDAP Name Service Switch Module
Summary(es.UTF-8):	Biblioteca NSS para LDAP
Summary(pl.UTF-8):	Moduł NSS LDAP
Summary(pt_BR.UTF-8):	Biblioteca NSS para LDAP
Name:		nss_ldapd
Version:	0.8.10
Release:	1
License:	LGPL
Group:		Base
Source0:	http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz
# Source0-md5:	8f76fefe50888bee09f7732102376342
Source1:	nslcd.init
Source2:	%{name}.tmpfiles
Patch0:		%{name}-no-root.patch
URL:		http://arthurdejong.org/nss-pam-ldapd/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	heimdal-devel
BuildRequires:	openldap-devel >= 2.3.0
BuildRequires:	pam-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	nslcd
Requires:	rc-scripts >= 0.2.0
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
Provides:	nslcd

%description nslcd
NSS LDAPD name service daemon.

%description nslcd -l pl.UTF-8
Demon serwisu nazw NSS LDAPD.

%package pam
Summary:	NSS LDAPD Pluggable Authentication Module
Summary(pl.UTF-8):	Moduł PAM do uwierzytelniania z użyciem NSS LDAPD
Group:		Base
Requires:	nslcd
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

%build
%configure \
	--with-pam-seclib-dir=/%{_lib}/security \
	--with-ldap-lib=openldap

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/rc.d/init.d,/var/run/nslcd} \
	$RPM_BUILD_ROOT/usr/lib/tmpfiles.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nslcd
install %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%pre nslcd
%useradd -u 21 -d /usr/share/empty -s /bin/false -c "NSS LDAP Cache Daemon User" -g nobody nslcd

%post nslcd
/sbin/chkconfig --add nslcd
%service nslcd restart "NSS LDAP Cache Daemon"

%preun nslcd
if [ "$1" = "0" ]; then
	%service nslcd stop
	/sbin/chkconfig --del nslcd
fi

%postun nslcd
if [ "$1" = "0" ]; then
	%userremove nslcd
fi

%triggerpostun nslcd -- nss_ldapd < 0.7.0
if [ -e %{_sysconfdir}/nss-ldapd.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/nslcd.conf{,rpmnew}
	mv -f %{_sysconfdir}/nss-ldapd.conf.rpmsave %{_sysconfdir}/nslcd.conf
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(755,root,root) %{_libdir}/*.so*

%files nslcd
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/nslcd
%attr(640,nslcd,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nslcd.conf
%attr(755,root,root) %{_sbindir}/nslcd
%{_mandir}/man5/nslcd.conf.5*
%{_mandir}/man8/nslcd.8*
%dir /var/run/nslcd
/usr/lib/tmpfiles.d/%{name}.conf

%files pam
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_ldap.so
%{_mandir}/man8/pam_ldap.8*
