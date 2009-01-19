Summary:	LDAP Name Service Switch Module
Summary(es.UTF-8):	Biblioteca NSS para LDAP
Summary(pl.UTF-8):	Moduł NSS LDAP
Summary(pt_BR.UTF-8):	Biblioteca NSS para LDAP
Name:		nss_ldapd
Version:	0.6.7
Release:	1
License:	LGPL
Group:		Base
Source0:	http://ch.tudelft.nl/~arthur/nss-ldapd/nss-ldapd-%{version}.tar.gz
# Source0-md5:	109257c0257b3119fa9a6a0fc1737f08
Source1:	nslcd.init
URL:		http://ch.tudelft.nl/~arthur/nss-ldapd/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	openldap-devel >= 2.4.6
Requires(post,preun):	/sbin/chkconfig
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

%prep
%setup -q -n nss-ldapd-%{version}

%build
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--with-ldap-lib=openldap
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_libdir},/etc/rc.d/init.d,/var/run/nslcd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nslcd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add nslcd
%service nslcd restart "NSS LDAP Cache Daemon"

%postun
if [ "$1" = "0" ]; then
	%service nslcd stop
	/sbin/chkconfig --del nslcd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(754,root,root) /etc/rc.d/init.d/nslcd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nss-ldapd.conf
%attr(755,root,root) %{_libdir}/*.so*
%attr(755,root,root) %{_sbindir}/nslcd
%{_mandir}/man5/*
%{_mandir}/man8/*
%dir /var/run/nslcd
