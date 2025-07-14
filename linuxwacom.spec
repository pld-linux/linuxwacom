# NOTE: this package is deprecated:
# - kernel module is in mainstream now
# - driver for xorg-xserver 1.7+ is in xorg-driver-input-wacom.spec
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# build kernel modules
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	userspace	# don't build userspace programs
%bcond_with	xorg		# X.org driver (now built from separate package, see xorg-driver-input-wacom.spec)
%bcond_with	hal		# HAL support (deprecated)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

Summary:	Wacom Drivers from Linux Wacom Project
Summary(pl.UTF-8):	Sterowniki Wacom z projektu Linux Wacom Project
Name:		linuxwacom
Version:	0.12.0
Release:	0.1
License:	GPL v2+
Group:		X11/Applications
Source0:	http://downloads.sourceforge.net/linuxwacom/%{name}-%{version}.tar.bz2
# Source0-md5:	b26cc71889656250be90cc8f43d535c4
Patch0:		%{name}-link.patch
URL:		http://linuxwacom.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	autoconf >= 2.58
BuildRequires:	automake
%{?with_hal:BuildRequires:	hal-devel >= 0.5.10}
BuildRequires:	libtool
BuildRequires:	ncurses-devel
BuildRequires:	pkgconfig
%{!?with_hal:BuildRequires:	sed >= 4.0}
BuildRequires:	tcl-devel
BuildRequires:	tk-devel
BuildRequires:	xorg-lib-libX11-devel
BuildRequires:	xorg-lib-libXi-devel
BuildRequires:	xorg-lib-libXrandr-devel
%{?with_xorg:BuildRequires:	xorg-lib-libpciaccess-devel}
%{?with_xorg:BuildRequires:	xorg-xserver-server-devel < 1.7}
%endif
Requires:	udev-core >= 030-21
Requires:	xorg-xserver-server
#ExclusiveArch:	%{ix86} %{x8664} alpha ia64 ppc sparc sparc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Linux Wacom Project manages the drivers, libraries, and
documentation for configuring and running Wacom tablets under the
Linux operating system. It contains diagnostic applications as well as
X.org XInput drivers.

%description -l pl.UTF-8
Linux Wacom Project utrzymuje sterowniki, biblioteki i dokumentację
do konfigurowania i uruchamiania tabletów Wacom pod systemem Linux.
Zawiera aplikacje diagnostyczne, a także sterowniki XInput do X.org.

%package tk
Summary:	Linux Wacom Tk library and utilities
Summary(pl.UTF-8):	Biblioteka i narzędzia Tk z projektu Linux Wacom
Group:		X11/Applications
Requires:	%{name} = %{version}-%{release}
Requires:	tk

%description tk
Linux Wacom Tk library and utilities.

%description tk -l pl.UTF-8
Biblioteka i narzędzia Tk z projektu Linux Wacom.

%package devel
Summary:	linuxwacom developmental header files
Summary(pl.UTF-8):	Pliki nagłówkowe linuxwacom
Group:		X11/Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Developmental header files required for developing or compiling
applications for manipulating settings for Wacom tablets.

%description devel -l pl.UTF-8
Pliki nagłówkowe potrzebne do tworzenia i kompilowania aplikacji
modyfikujących ustawienia tabletów Wacom.

%package static
Summary:	linuxwacom static library
Summary(pl.UTF-8):	Statyczna biblioteka linuxwacom
Group:		X11/Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
linuxwacom static library.

%description static -l pl.UTF-8
Statyczna biblioteka linuxwacom.

%package -n xorg-driver-input-wacom
Summary:	X.org input driver for Wacom tablets
Summary(pl.UTF-8):	Sterownik wejściowy X.org dla tabletów Wacom
Group:		X11/Applications
%requires_xorg_xserver_xinput
Conflicts:	linuxwacom < 0.12.0

%description -n xorg-driver-input-wacom
X.org input driver for Wacom tablets.

%description -n xorg-driver-input-wacom -l pl.UTF-8
Sterownik wejściowy X.org dla tabletów Wacom.

%prep
%setup -q
%patch -P0 -p1

%if %{with kernel}
cat > src/2.6.30/Makefile << EOF
obj-m += wacom.o
wacom-objs := wacom_wac.o wacom_sys.o
%{?debug:CFLAGS += -DCONFIG_MODULE_NAME_DEBUG=1}
EOF
%endif

%if %{without hal}
%{__sed} -i -e 's/hal >= /DISABLED_hal >= /' configure.in
%endif

%build
%if %{with kernel}
%build_kernel_modules -C src/2.6.30 -m wacom
%endif

%if %{with userspace}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

export CFLAGS="-I/usr/include/ncurses %{rpmcflags}"
%configure \
	%{!?with_xorg:--disable-wacomdrv --disable-xsetwacom} \
	--without-kernel \
	%{!?with_xorg:--without-xorg-sdk}

%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	x86moduledir=%{_libdir}/xorg/modules/input

%if %{with xorg}
install -D src/util/60-wacom.rules $RPM_BUILD_ROOT/lib/udev/rules.d/60-wacom.rules
%endif

%{__rm} $RPM_BUILD_ROOT%{_libdir}/TkXInput/libwacomxi.{la,a}
%endif

%if %{with kernel}
%install_kernel_modules -m src/2.6.30/wacom -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README
%attr(755,root,root) %{_bindir}/wacdump
%attr(755,root,root) %{_bindir}/xidump
%attr(755,root,root) %{_libdir}/libwacomcfg.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libwacomcfg.so.0
%if %{with hal}
%{_libexecdir}/hal-setup-wacom
%{_datadir}/hal/fdi/policy/20thirdparty/10-linuxwacom.fdi
%endif

%files tk
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/wacomcpl
%attr(755,root,root) %{_bindir}/wacomcpl-exec
%dir %{_libdir}/TkXInput
%attr(755,root,root) %{_libdir}/TkXInput/libwacomxi.so*
%{_libdir}/TkXInput/pkgIndex.tcl

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwacomcfg.so
%{_libdir}/libwacomcfg.la
%{_includedir}/wacomcfg

%files static
%defattr(644,root,root,755)
%{_libdir}/libwacomcfg.a

%if %{with xorg}
%files -n xorg-driver-input-wacom
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/xsetwacom
%attr(755,root,root) %{_libdir}/xorg/modules/input/wacom_drv.so
/lib/udev/rules.d/60-wacom.rules
%{_mandir}/man4/wacom.4*
%{_mandir}/man4/xsetwacom.4*
%endif
%endif
