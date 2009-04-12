#
# NOTE: kernel module is in mainstream now
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

Summary:	Wacom Drivers from Linux Wacom Project
Summary(pl.UTF-8):	Sterowniki Wacom z projektu Linux Wacom Project
Name:		linuxwacom
Version:	0.8.3
Release:	1
License:	GPL/X11
Group:		X11
Source0:	http://dl.sourceforge.net/linuxwacom/%{name}-%{version}-2.tar.bz2
# Source0-md5:	3126718ca78a0c35c3d62d25817c8ece
Source1:	%{name}-rules
URL:		http://linuxwacom.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	ncurses-devel
BuildRequires:	tcl-devel
BuildRequires:	tk-devel
BuildRequires:	xorg-lib-libX11-devel
BuildRequires:	xorg-lib-libXi-devel
BuildRequires:	xorg-lib-libpciaccess-devel
BuildRequires:	xorg-xserver-server-devel
%endif
Requires:	udev-core >= 030-21
Requires:	xorg-xserver-server
#ExclusiveArch:	%{ix86} %{x8664} alpha ia64 ppc sparc sparc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_x11sdkdir	%(pkg-config --variable=sdkdir xorg-server)

%description
The Linux Wacom Project manages the drivers, libraries, and
documentation for configuring and running Wacom tablets under the
Linux operating system. It contains diagnostic applications as well as
X.org XInput drivers.

%description -l pl.UTF-8
Linux Wacom Project utrzymuje sterowniki, biblioteki i dokumentację
do konfigurowania i uruchamiania tabletów Wacom pod systemem Linux.
Zawiera aplikacje diagnostyczne, a także sterowniki XInput do X.org.

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

%prep
%setup -q -n %{name}-%{version}-2

cat > src/2.6.19/Makefile << EOF
obj-m += wacom.o
wacom-objs := wacom_wac.o wacom_sys.o
%{?debug:CFLAGS += -DCONFIG_MODULE_NAME_DEBUG=1}
EOF
cp src/2.6.1{6,9}/wacom_wac.h

%build
%if %{with kernel}
%build_kernel_modules -C src/2.6.19 -m wacom
%endif

%if %{with userspace}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

#X SERVER64=
#if [ "$(getconf LONG_BIT)" == "64" ]; then
#	XSERVER64=--enable-xserver64
#fi
export CFLAGS="-I/usr/include/ncurses %{rpmcflags}"
%configure \
	--with-gtk \
	--with-tcl \
	--with-tk \
	--enable-wacomxi \
	--enable-libwacomxi \
	--with-xorg-sdk \
	--with-xlib \
	--enable-dlloader \
	--with-x \
	--enable-wacdump \
	--enable-xidump \
	--enable-libwacomcfg \
	--enable-xsetwacom \
	--enable-tabletdev \
	--enable-wacomdrv
# --enable-xserver64	Use specified X server bit [default=usually]
# --enable-mkxincludes	Enable mkxincludes, XF86 dependency builder [default=no]
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	x86moduledir=%{_libdir}/xorg/modules/input

#install src/xdrv/wacom_drv.so $RPM_BUILD_ROOT%{_libdir}/xorg/modules/input
install -D %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/10-wacom.rules
rm -f $RPM_BUILD_ROOT%{_libdir}/TkXInput/libwacomxi.{la,a}
%endif

%if %{with kernel}
%install_kernel_modules -m src/2.6.19/wacom -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%if %{with userspace}
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README NEWS
%attr(755,root,root) %{_bindir}/wacdump
%attr(755,root,root) %{_bindir}/wacomcpl*
%attr(755,root,root) %{_bindir}/xidump
%attr(755,root,root) %{_bindir}/xsetwacom
%attr(755,root,root) %{_libdir}/libwacomcfg*.so.*.*.*
%dir %{_libdir}/TkXInput
%attr(755,root,root) %{_libdir}/TkXInput/libwacomxi.so*
%{_libdir}/TkXInput/pkgIndex.tcl
%{_mandir}/man4/*.4*
%attr(755,root,root) %{_libdir}/libwacomcfg.so.0
%attr(755,root,root) %{_libdir}/xorg/modules/input/wacom_drv.so
%{_sysconfdir}/udev/rules.d/10-wacom.rules
%{_libdir}/hal-setup-wacom
%{_datadir}/hal/fdi/policy/20thirdparty/10-linuxwacom.fdi

#%%files tk
#%attr(755,root,root) %{_bindir}/wacomcpl
#%attr(755,root,root) %{_bindir}/wacomcpl-exec
#%dir %{_libdir}/TkXInput
#%attr(755,root,root) %{_libdir}/TkXInput/libwacomxi.so*
#%{_libdir}/TkXInput/pkgIndex.tcl

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwacomcfg*.so
%{_libdir}/libwacomcfg*.la
%dir %{_includedir}/wacomcfg
%{_includedir}/wacomcfg/wacomcfg.h

%files static
%defattr(644,root,root,755)
%{_libdir}/libwacomcfg*.a
%endif
