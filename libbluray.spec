%global tarball_date 20110126
%global git_hash bbf11e43bd82eabce8a4f8aa3ec09bccef18de2e
%global git_short %(echo '%{git_hash}' | cut -c -13)

%global static_build 0

Name:           libbluray
Version:        0.2
Release:        0.2.%{tarball_date}git%{git_short}%{?dist}
Summary:        Library to access Blu-Ray disks for video playback 
Group:          System Environment/Libraries
License:        LGPLv2+
URL:            http://www.videolan.org/developers/libbluray.html
# No release yet. Use the commands below to generate a tarball.
# git clone git://git.videolan.org/libbluray.git
# cd libbluray
# git archive --format=tar %{git_hash} --prefix=libbluray/ | bzip2 > ../libbluray-$( date +%Y%m%d )git%{git_short}.tar.bz2
Source0:        %{name}-%{tarball_date}git%{git_short}.tar.bz2
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  java-1.6.0-devel
BuildRequires:  jpackage-utils
BuildRequires:  ant
BuildRequires:  libxml2-devel
BuildRequires:  doxygen
BuildRequires:  texlive-latex
BuildRequires:  graphviz


%description
This package is aiming to provide a full portable free open source bluray
library, which can be plugged into popular media players to allow full bluray
navigation and playback on Linux. It will eventually be compatible with all
current titles, and will be easily portable and embeddable in standard players
such as mplayer and vlc.


%package        java
Summary:        BDJ support for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       java-1.6.0
Requires:       jpackage-utils

%description    java
The %{name}-java package contains the jar file needed to add BDJ support to
%{name}.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{static_build}
%package        static
Summary:        Static lib for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    static
The %{name}-static package contains static libraries.
%endif


%prep
%setup -q -n %{name}


%build
autoreconf -vif
# Some of the examples need the static lib to build.
# Don't build them if not building the static lib too.
%configure \
%if !%{static_build}
           --disable-static \
           --disable-examples \
%else
           --enable-examples \
%endif
           --with-jdk=%{_jvmdir}/java-1.6.0 \
           --enable-bdjava
make %{?_smp_mflags}
make doxygen-pdf
# Remove uneeded script
rm doc/doxygen/html/installdox


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

install -Dp -m 644 src/.libs/libbluray.jar  $RPM_BUILD_ROOT%{_javadir}/libbluray.jar

# Install test utilities
%if %{static_build}
for i in mpls_dump clpi_dump index_dump mobj_dump sound_dump 
do install -Dp -m 0755 src/examples/$i $RPM_BUILD_ROOT%{_bindir}/$i; done;
for i in bdsplice libbluray_test list_titles hdmv_test bdj_test bd_info
do install -Dp -m 0755 src/examples/.libs/$i $RPM_BUILD_ROOT%{_bindir}/$i; done;
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING doc/README player_wrappers README.txt TODO.txt
%{_libdir}/*.so.*


%files java
%defattr(-,root,root,-)
%{_javadir}/libbluray.jar


%files devel
%defattr(-,root,root,-)
%doc doc/doxygen/html doc/doxygen/libbluray.pdf
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libbluray.pc


%if %{static_build}
%files static
%defattr(-,root,root,-)
%{_libdir}/libbluray.a
%{_bindir}/*
%endif


%changelog
* Wed Jan 26 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.2.20110126gitbbf11e43bd82e
- Update to latest snapshot.
- Split the BDJ support to a -java subpackage.

* Fri Jan 07 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.1.20110107git0e5902ff9a6f1
- Update to latest snapshot.
- Add BR: libxml2-devel for metadata parser.
- Add BR: graphviz for doc generation.

* Thu Oct 28 2010 Xavier Bachelot <xavier@bachelot.org> 0.1-0.3.20101028gitc32862b77dea4
- Update to latest snapshot.
- Install BDJ jar.

* Thu Oct 21 2010 Xavier Bachelot <xavier@bachelot.org> 0.1-0.2.20101021git144a204c02687
- Fix release tag.
- Update to latest snapshot.

* Thu Aug 19 2010 Xavier Bachelot <xavier@bachelot.org> 0.1-0.1.20100819
- Initial Fedora release.
