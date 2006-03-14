%define _x11dir		%{_prefix}
%define _x11libdir	%{_x11dir}/%{_lib}
%define _x11sdkdir	%(pkg-config --variable=sdkdir xorg-server)

Name:		linuxwacom
Version:	0.7.2
Release:	0.1
Summary:	Wacom Drivers from Linux Wacom Project

Group:		User Interface/X Hardware Support
######		Unknown group!
License:	GPL/X11
URL:		http://linuxwacom.sourceforge.net
Source0:	http://dl.sourceforge.net/linuxwacom/%{name}-%{version}.tar.bz2
Source1:	10-wacom.rules
Patch2:		%{name}-fsp.patch
Patch3:		%{name}-0.7.2-modular-sdk.patch

BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	aLotOfWork
Requires:	inKernel2.6.14NeedsNewHidAndWacomModule
#BuildRequires:	libX11-devel, libXi-devel, xorg-x11-server-sdk, ncurses-devel
#Requires:	Xserver, udev >= 030-21
#ExclusiveArch:  %{ix86} x86_64 alpha ia64 ppc sparc sparc64

%description
The Linux Wacom Project manages the drivers, libraries, and
documentation for configuring and running Wacom tablets under the
Linux operating system. It contains diagnostic applications as well as
X.org XInput drivers.

%package devel
Summary:	linuxwacom developmental libraries and header files
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Developmental libraries and header files required for developing or
compiling applications for manipulating settings for Wacom tablets.

%prep
%setup -q

%patch2 -p1 -b .fsp
%patch3 -p0 -b .modular-sdk

%build
#libtoolize --copy --force
#aclocal
#autoconf
#automake --foreign

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
	--enable-dlloader
#	$XSERVER64


%{__make}
    XORG_SDK_DIR=%{_x11sdkdir}

%install
rm -rf $RPM_BUILD_ROOT

install -d \
	$RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d \
	$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
	x86moduledir=$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

install src/wacom_drv.so $RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/10-wacom.rules
rm $RPM_BUILD_ROOT/%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README NEWS
%attr(444,root,root) %{_x11libdir}/xorg/modules/input/wacom_drv.so
%attr(755,root,root) %{_bindir}/wacdump
%attr(755,root,root) %{_bindir}/xidump
%attr(755,root,root) %{_bindir}/xsetwacom
%{_libdir}/libwacomcfg*so.*
%{_sysconfdir}/udev/rules.d/10-wacom.rules

%files devel
%defattr(644,root,root,755)
%{_includedir}/wacomcfg/wacomcfg.h
%{_libdir}/libwacomcfg*.a
%attr(755,root,root) %{_libdir}/libwacomcfg*.so
