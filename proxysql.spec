Summary:	A high-performance MySQL proxy
Name:		proxysql
Version:	1.3.7
Release:	0.1
# The entire source code is GPLv3+ except deps/re2 and deps/jemalloc which is BSD
# and deps/mariadb-connector-c which is LGPLv2+
License:	GPLv3+ and LGPLv2+ and BSD
Group:		Development/Tools
Source0:	https://github.com/sysown/proxysql/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0698bb3f4daec5f80dacdf5011f6ac80
Source1:	%{name}.service
Source2:	%{name}.1
Patch0:		%{name}_debundle_libconfig_libdaemon_sqlite3.patch
URL:		http://www.proxysql.com/
BuildRequires:	cmake
BuildRequires:	libconfig-devel
BuildRequires:	libdaemon-devel
BuildRequires:	openssl-devel
BuildRequires:	sqlite-devel
BuildRequires:	systemd-devel
Provides:	bundled(jemalloc) = 4.3.1
Provides:	bundled(mariadb-connector-c) = 2.3.1
Provides:	bundled(re2) = 20140304
# Build in other architectures aside from x86 is not yet supported due to some
# use of assembly code, but is on the upstream roadmap to support them.
# https://github.com/sysown/proxysql/issues/977
ExcludeArch:	%{arm} %{power64} s390x aarch64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ProxySQL is a high performance, high availability, protocol aware
proxy for MySQL and forks (like Percona Server and MariaDB).

%prep
%setup -q
%patch0 -p1

rm -r deps/libconfig deps/libdaemon deps/sqlite3

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -p -D src/proxysql -t $RPM_BUILD_ROOT%{_bindir}
install -p -D etc/proxysql.cnf -t $RPM_BUILD_ROOT%{_sysconfdir}
install -p -D tools/proxysql_galera_checker.sh -t $RPM_BUILD_ROOT%{_datadir}/%{name}/tools
install -p -D tools/proxysql_galera_writer.pl -t $RPM_BUILD_ROOT%{_datadir}/%{name}/tools
install -p -D %{SOURCE1} -t $RPM_BUILD_ROOT%{systemdunitdir}
install -p -D README.md -t $RPM_BUILD_ROOT%{_docdir}/proxysql
install -p -D RUNNING.md -t $RPM_BUILD_ROOT%{_docdir}/proxysql
install -p -D FAQ.md -t $RPM_BUILD_ROOT%{_docdir}/proxysql
install -p -D doc/*.md -t $RPM_BUILD_ROOT%{_docdir}/proxysql
install -p -D %{SOURCE2} -t $RPM_BUILD_ROOT%{_mandir}/man1
install -d -D $RPM_BUILD_ROOT%{_sharedstatedir}/proxysql

%if 0
%pre
/usr/sbin/groupadd -r proxysql >/dev/null 2>&1 || :
%useradd  -g proxysql -r -d /var/lib/proxysql -s /sbin/nologin     -c "ProxySQL" proxysql >/dev/null 2>&1 || :
%endif

%post
%systemd_post proxysql.service

%preun
%systemd_preun proxysql.service

%postun
%systemd_postun_with_restart proxysql.service

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE
%attr(755,root,root) %{_bindir}/*
%{systemdunitdir}/*
%{_datadir}/%{name}
%{_docdir}/%{name}
%{_mandir}/man1/*
%defattr(-,proxysql,proxysql,-)
%{_sharedstatedir}/%{name}
%defattr(-,proxysql,root,-)
%config(noreplace) %{_sysconfdir}/%{name}.cnf
