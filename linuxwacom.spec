%bcond_without  dist_kernel     # allow non-distribution kernel
%bcond_without  kernel          # don't build kernel modules
%bcond_without  smp             # don't build SMP module
%bcond_without  userspace       # don't build userspace programs
%bcond_with     verbose         # verbose build (V=1)

%if %{without kernel}
%undefine       with_dist_kernel
%endif

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
Patch1:		%{name}-xorg-7.patch
#Patch3:		%{name}-0.7.2-modular-sdk.patch
URL:		http://linuxwacom.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:      kernel%{_alt_kernel}-module-build >= 3:2.6.14}
%{?with_dist_kernel:BuildRequires:      kernel-source }

BuildRequires:  rpmbuild(macros) >= 1.308
%endif
#BuildRequires:	
Requires(post,postun):  /sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):       %releq_kernel_up

BuildRequires:	tk-devel
BuildRequires:	tcl-devel
BuildRequires:	xorg-lib-libX11-devel
BuildRequires:	xorg-lib-libXi-devel
BuildRequires:	ncurses-devel
Requires:	Xserver
Requires:	udev >= 030-21
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
Linux Wacom Project utrzymuje sterowniki, biblioteki i dokumentacjê do
konfigurowania i uruchamiania tabletów Wacom pod systemem Linux.
Zawiera aplikacje diagnostyczne, a tak¿e sterowniki XInput do X.org.

%package devel
Summary:	linuxwacom developmental header files
Summary(pl):	Pliki nag³ówkowe linuxwacom
Group:		X11/Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Developmental header files required for developing or compiling
applications for manipulating settings for Wacom tablets.

%description devel -l pl
Pliki nag³ówkowe potrzebne do tworzenia i kompilowania aplikacji
modyfikuj±cych ustawienia tabletów Wacom.

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
%patch1 -p1
#%patch3 -p0

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

#X SERVER64=
#if [ "$(getconf LONG_BIT)" == "64" ]; then
#	XSERVER64=--enable-xserver64
#fi

#export RPM_LIBDIR=%{_lib}
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
	--enable-tabletdev \
	--enable-wacomdrv \
	--enable-modver \
	--with-kernel=%{_kernelsrcdir} \
	--enable-hid \
	--enable-wacom

# for 2.4 only	--enable-usbmouse
# for 2.4 only	--enable-input
# for 2.4 only	--enable-mousedev
# for 2.4 only  --enable-evdev
# --enable-xserver64	Use specified X server bit [default=usually]
# --enable-mkxincludes	Enable mkxincludes, XF86 dependency builder [default=no]
# --with-xmoduledir	Specify wacom_drv path explicitly. Implies --enable-dlloader
%if %{with userspace}


%endif

%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
        if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
                exit 1
        fi
        install -d o/include/linux
        ln -sf %{_kernelsrcdir}/config-$cfg o/.config
        ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
        ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
        %{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts XORG_SDK_DIR=%{_x11sdkdir}
%else
        install -d o/include/config
        touch o/include/config/MARKER
        ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif

done
%endif


%install
rm -rf $RPM_BUILD_ROOT

install -d \
	$RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d \
	$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	x86moduledir=$RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

%if %{with userspace}


%endif

#%%if %{with kernel}
#install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/MODULE_DIR
#install MODULE_NAME-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
#        $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/MODULE_DIR/MODULE_NAME.ko
#%%if %{with smp} && %{with dist_kernel}
#install MODULE_NAME-smp.ko \
#        $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/MODULE_DIR/MODULE_NAME.ko
#%%endif
#%%endif




install src/wacom_drv.so $RPM_BUILD_ROOT%{_x11libdir}/xorg/modules/input

#install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/10-wacom.rules

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
%%attr(755,root,root) %{_x11libdir}/xorg/modules/input/wacom_drv.so
#%%{_sysconfdir}/udev/rules.d/10-wacom.rules

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwacomcfg*.so
%{_libdir}/libwacomcfg*.la
%dir %{_includedir}/wacomcfg
%{_includedir}/wacomcfg/wacomcfg.h

%files static
%defattr(644,root,root,755)
%{_libdir}/libwacomcfg*.a
