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
URL:		http://ch.tudelft.nl/~arthur/nss-ldapd/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cyrus-sasl-devel
BuildRequires:	openldap-devel >= 2.4.6
Requires:	openldap-nss-config
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		/%{_lib}

%description
nss_ldapd is a C library extension (NSS module) and daemon which
allows X.500 and LDAP directory servers to be used as a primary source
of aliases, ethers, groups, hosts, networks, protocols, users, RPCs,
services and shadow passwords (instead of or in addition to using flat
files or NIS).

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
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_libdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(755,root,root) %{_libdir}/*.so*
%{_sysconfdir}/nss-ldapd.conf
%attr(755,root,root) %{_sbindir}/nslcd
%{_mandir}/man5/*
%{_mandir}/man8/*
