Summary:	Wacom Drivers from Linux Wacom Project
Summary(pl):	Sterowniki Wacom z projektu Linux Wacom Project
Name:		linuxwacom
Version:	0.7.4
Release:	0.1
Group:		X11
License:	GPL/X11
Source0:	http://dl.sourceforge.net/linuxwacom/%{name}-%{version}-3.tar.bz2
# Source0-md5:	9414aa852c97b8addb32481db04be9e5
#Source1:	10-wacom.rules
#Patch2:		%{name}-fsp.patch
#Patch3:		%{name}-0.7.2-modular-sdk.patch
URL:		http://linuxwacom.sourceforge.net/
#BuildRequires:	aLotOfWork
#Requires:	inKernel2.6.14NeedsNewHidAndWacomModule
BuildRequires:	xorg-lib-libX11-devel
BuildRequires:	xorg-lib-libXi-devel
BuildRequires:	xorg-x11-server-sdk
BuildRequires:	ncurses-devel
#Requires:	Xserver, udev >= 030-21
#ExclusiveArch:	%{ix86} %{x8664} alpha ia64 ppc sparc sparc64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_x11dir		%{_prefix}
%define		_x11libdir	%{_x11dir}/%{_lib}
%define		_x11sdkdir	%(pkg-config --variable=sdkdir xorg-server)

%description
The Linux Wacom Project manages the drivers, libraries, and
documentation for configuring and running Wacom tablets under the
Linux operating system. It contains diagnostic applications as well as
X.org XInput drivers.

%description -l pl
Linux Wacom Project utrzymuje sterowniki, biblioteki i dokumentację do
konfigurowania i uruchamiania tabletów Wacom pod systemem Linux.
Zawiera aplikacje diagnostyczne, a także sterowniki XInput do X.org.

%package devel
Summary:	linuxwacom developmental header files
Summary(pl):	Pliki nagłówkowe linuxwacom
Group:		X11/Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Developmental header files required for developing or compiling
applications for manipulating settings for Wacom tablets.

%description devel -l pl
Pliki nagłówkowe potrzebne do tworzenia i kompilowania aplikacji
modyfikujących ustawienia tabletów Wacom.

%package static
Summary:	linuxwacom static library
Summary(pl):	Statyczna biblioteka linuxwacom
Group:		X11/Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
linuxwacom static library.

%description static -l pl
Statyczna biblioteka linuxwacom.

%prep
%setup -q -n %{name}-%{version}-3
#%patch2 -p1
#%patch3 -p0

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

#X SERVER64=
#if [ "$(getconf LONG_BIT)" == "64" ]
#then
#  XSERVER64=--enable-xserver64
#fi

#export RPM_LIBDIR=%{_lib}
export CFLAGS="-I%{_includedir}/ncurses %{rpmcflags}"
%configure \
	--without-gtk \
	--without-tcl \
	--without-tk \
	--disable-wacomxi \
	--disable-libwacomxi \
	--with-xorg-sdk=%{_x11sdkdir} \
	--with-xlib=%{_x11libdir} \
	--enable-dlloader \
	--with-x \
	--enable-wacom \
	--enable-wacdump \
	--enable-xidump \
	--enable-libwacomcfg \
	--enable-xsetwacom \
	--enable-libwacomxi \
	--enable-hid \
	--enable-evdev \
	--enable-tabletdev \
	--enable-wacomdrv \
	--enable-modver \
	--with-kernel=%{_kernelsrcdir}


#	--with-xorg-sdk=dir
# for 2.4 only	--enable-usbmouse
# for 2.4 only	--enable-input
# for 2.4 only	--enable-mousedev
# --enable-xserver64      Use specified X server bit [default=usually]
# --enable-mkxincludes    Enable mkxincludes, XF86 dependency builder [default=no]
#  --with-x-src=dir        Specify X driver build directory
#  --with-xorg-sdk=dir     Specify Xorg SDK directory
#  --with-xlib=dir         uses a specified X11R6 directory
#  --with-tcl=dir          uses a specified tcl directory
#  --with-tk=dir           uses a specified tk directory
#  --with-xmoduledir       Specify wacom_drv path explicitly. Implies --enable-dlloader


%{__make} \
	XORG_SDK_DIR=%{_x11sdkdir}

%install
rm -rf $RPM_BUILD_ROOT

install -d \
	$RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d \
	$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	x86moduledir=$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

install src/wacom_drv.so $RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/10-wacom.rules

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README NEWS
%attr(755,root,root) %{_bindir}/wacdump
%attr(755,root,root) %{_bindir}/xidump
%attr(755,root,root) %{_bindir}/xsetwacom
%attr(755,root,root) %{_libdir}/libwacomcfg*.so.*.*.*
%attr(755,root,root) %{_x11libdir}/xorg/modules/input/wacom_drv.so
%{_sysconfdir}/udev/rules.d/10-wacom.rules

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwacomcfg*.so
%{_libdir}/libwacomcfg*.la
%dir %{_includedir}/wacomcfg
%{_includedir}/wacomcfg/wacomcfg.h

%files static
%defattr(644,root,root,755)
%{_libdir}/libwacomcfg*.a
