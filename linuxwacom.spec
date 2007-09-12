# TODO
# - no package for kernel modules, even if they're built
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%define		relver		3
%if %{without kernel}
%undefine	with_dist_kernel
%endif

Summary:	Wacom Drivers from Linux Wacom Project
Summary(pl.UTF-8):	Sterowniki Wacom z projektu Linux Wacom Project
Name:		linuxwacom
Version:	0.7.8
Release:	1
Group:		X11
License:	GPL/X11
Source0:	http://dl.sourceforge.net/linuxwacom/%{name}-%{version}-%{relver}.tar.bz2
# Source0-md5:	19214c30e68114bb2101a287b11b8f32
Source1:	linuxwacom-rules
URL:		http://linuxwacom.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:  rpmbuild(macros) >= 1.308
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
BuildRequires:	xorg-xserver-server-devel
%endif
Requires:	xorg-xserver-server
Requires:	udev >= 030-21
#ExclusiveArch:	%{ix86} %{x8664} alpha ia64 ppc sparc sparc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_x11sdkdir	%(pkg-config --variable=sdkdir xorg-server)

%description
The Linux Wacom Project manages the drivers, libraries, and
documentation for configuring and running Wacom tablets under the
Linux operating system. It contains diagnostic applications as well as
X.org XInput drivers.

%description -l pl.UTF-8
Linux Wacom Project utrzymuje sterowniki, biblioteki i dokumentację do
konfigurowania i uruchamiania tabletów Wacom pod systemem Linux.
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
%setup -q -n %{name}-%{version}-%{relver}

%build
%if %{with userspace}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

#X SERVER64=
#if [ "$(getconf LONG_BIT)" == "64" ]; then
#	XSERVER64=--enable-xserver64
#fi
export CFLAGS="-I%{_includedir}/ncurses %{rpmcflags}"
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
	--enable-libwacomxi \
	--disable-tabletdev \
	--disable-wacomdrv \
	--enable-modver \
	--disable-wacom

#-with-kernel=%{_kernelsrcdir}
#-enable-hid
# for 2.4 only	--enable-usbmouse
# for 2.4 only	--enable-input
# for 2.4 only	--enable-mousedev
# for 2.4 only  --enable-evdev
# --enable-xserver64	Use specified X server bit [default=usually]
# --enable-mkxincludes	Enable mkxincludes, XF86 dependency builder [default=no]
# --with-xmoduledir	Specify wacom_drv path explicitly. Implies --enable-dlloader
%{__make}
%endif

%if %{with kernel}
%build_kernel_modules -m wacom
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d \
	$RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d \
	$RPM_BUILD_ROOT%{_libdir}/xorg/modules/input

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	x86moduledir=$RPM_BUILD_ROOT%{_libdir}/xorg/modules/input

%if %{with userspace}
rm -f $RPM_BUILD_ROOT%{_libdir}/TkXInput/libwacomxi.{la,a}
%endif

%if %{with kernel}
install src/xdrv/wacom_drv.so $RPM_BUILD_ROOT%{_libdir}/xorg/modules/input
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/10-wacom.rules
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
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
%if %{with kernel}
%attr(755,root,root) %{_libdir}/xorg/modules/input/wacom_drv.so
%{_sysconfdir}/udev/rules.d/10-wacom.rules
%endif

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
