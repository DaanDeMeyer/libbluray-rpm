#global snapshot 1
%global tarball_date 20130427
%global git_hash 2b002fe52e8c2506ed52bf56c8b517d350dbb281
%global git_short %(echo '%{git_hash}' | cut -c -13)
%global build_pdf_doc 0

Name:           libbluray
Version:        0.6.0
Release:        1%{?snapshot:.%{tarball_date}git%{git_short}}%{?dist}
Summary:        Library to access Blu-Ray disks for video playback 
License:        LGPLv2+
URL:            http://www.videolan.org/developers/libbluray.html
%if 0%{?snapshot}
# Use the commands below to generate a tarball.
# git clone git://git.videolan.org/libbluray.git
# cd libbluray
# git archive --format=tar %{git_hash} --prefix=libbluray/ | bzip2 > ../libbluray-$( date +%Y%m%d )git%{git_short}.tar.bz2
Source0:        %{name}-%{tarball_date}git%{git_short}.tar.bz2
%else
Source0:        ftp://ftp.videolan.org/pub/videolan/%{name}/%{version}/%{name}-%{version}.tar.bz2
%endif
Patch0:         libbluray-0.2.2-no_doxygen_timestamp.patch

%if 0%{?snapshot}
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
%endif
%ifnarch ppc ppc64 ppc64le
%if 0%{?rhel} >= 6
BuildRequires:  java7-devel >= 1:1.7.0 
%else
BuildRequires:  java-devel >= 1:1.7.0
%endif
BuildRequires:  jpackage-utils
BuildRequires:  ant
%endif
BuildRequires:  libxml2-devel
BuildRequires:  doxygen
BuildRequires:  texlive-latex
BuildRequires:  graphviz
BuildRequires:  freetype-devel


%description
This package is aiming to provide a full portable free open source bluray
library, which can be plugged into popular media players to allow full bluray
navigation and playback on Linux. It will eventually be compatible with all
current titles, and will be easily portable and embeddable in standard players
such as mplayer and vlc.


%ifnarch ppc ppc64 ppc64le
%package        bdj
Summary:        BDJ support for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%if 0%{?fedora} > 20
Requires:       java-headless >= 1:1.7.0
%else
Requires:       java >= 1:1.7.0
%endif
Requires:       jpackage-utils
Obsoletes:      libbluray-java < 0.4.0-2
Provides:       libbluray-java = %{version}-%{release}

%description    bdj
The %{name}-bdj package contains the jar file needed to add BD-J support to
%{name}.
BD-J support is still considered alpha.
%endif

%package utils
Summary:        Test utilities for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description utils
The %{name}-utils package contains test utilities for %{name}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%if 0%{?snapshot}
%setup -q -n %{name}
%else
%setup -q
%endif
%patch0 -p1 -b .no_timestamp


%build
%if 0%{?snapshot}
autoreconf -vif
%endif
export JDK_HOME="%{_jvmdir}/java-1.7.0"
%configure --disable-static \
%if %{build_pdf_doc}
           --enable-doxygen-pdf \
%else
           --disable-doxygen-pdf \
%endif
           --disable-doxygen-ps \
           --enable-doxygen-html \
           --enable-examples \
%ifnarch ppc ppc64 ppc64le
           --enable-bdjava
%endif

# Fix rpath issue
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}
make doxygen-doc
# Remove uneeded script
rm -f doc/doxygen/html/installdox 


%install
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# Install test utilities
for i in bdsplice clpi_dump hdmv_test index_dump libbluray_test \
         list_titles mobj_dump mpls_dump sound_dump
do install -Dp -m 0755 src/$i $RPM_BUILD_ROOT%{_bindir}/$i; done;

%ifnarch ppc ppc64 ppc64le
install -Dp -m755 src/bdj_test %{buildroot}%{_bindir}/bdj_test;
%endif


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc COPYING README.txt
%{_libdir}/*.so.*

%ifnarch ppc ppc64 ppc64le
%files bdj
%{_javadir}/libbluray-j2se-%{version}.jar
%endif

%files utils
%{_bindir}/*

%files devel
%doc doc/doxygen/html
%if %{build_pdf_doc}
%doc doc/doxygen/libbluray.pdf
%endif
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libbluray.pc


%changelog
* Wed Jun 04 2014 Xavier Bachelot <xavier@bachelot.org> 0.6.0-1
- Update to 0.6.0.

* Sat Apr 26 2014 Xavier Bachelot <xavier@bachelot.org> 0.5.0-5
- Tweak the Release: tag to accomodate rpmdev-bumpspec.

* Fri Feb 21 2014 Xavier Bachelot <xavier@bachelot.org> 0.5.0-4
- Requires: java-headless for Fedora 21+ (RHBZ#1068351).
- Modernize specfile.

* Fri Jan 10 2014 Xavier Bachelot <xavier@bachelot.org> 0.5.0-3
- Disable BD-J support for ppc64le arch (RHBZ#1051604).

* Sun Dec 22 2013 Xavier Bachelot <xavier@bachelot.org> 0.5.0-2
- Fix build on EL6 (BR: java7-devel instead of java-devel).

* Sat Dec 21 2013 Xavier Bachelot <xavier@bachelot.org> 0.5.0-1
- Update to 0.5.0.

* Tue Nov 26 2013 Xavier Bachelot <xavier@bachelot.org> 0.4.0-2
- Move test utilities to their own subpackage to avoid multilib conflict.
  Fix RHBZ#1034307.
- Rename java subpackage to bdj.
- Remove obsolete xine-lib bluray input plugin from doc files.

* Fri Sep 20 2013 Xavier Bachelot <xavier@bachelot.org> 0.4.0-1
- Update to 0.4.0.
- Fix rpath issues with some test utilities.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Aug 21 2012 Xavier Bachelot <xavier@bachelot.org> 0.2.3-1
- Update to 0.2.3.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 12 2012 Xavier Bachelot <xavier@bachelot.org> 0.2.2-3
- Don't build pdf doc, it breaks multilib (see RHBZ#835952).

* Tue Jun 12 2012 Xavier Bachelot <xavier@bachelot.org> 0.2.2-2
- Fix multilib conflict in doxygen docs (RHBZ#831401).

* Tue Mar 20 2012 Xavier Bachelot <xavier@bachelot.org> 0.2.2-1
- Update to 0.2.2.

* Tue Mar 20 2012 Karsten Hopp <karsten@redhat.com> 0.2.1-4
- ppc(64) has no java-1.7.0-open yet, disable java subpackage on both PPC archs

* Thu Mar 15 2012 Rex Dieter <rdieter@fedoraproject.org> 0.2.1-3
- make build non-fatal when using doxygen-1.8 (doesn't produce installdox anymore)

* Wed Feb 01 2012 Xavier Bachelot <xavier@bachelot.org> 0.2.1-2
- Rebuild for openjdk 7.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 01 2011 Xavier Bachelot <xavier@bachelot.org> 0.2.1-1
- First upstream official release.
- Fix BD-J build (missing files in upstream tarball).
- Have subpackages require an arch-specific base package.

* Sun Oct 23 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.7.20111023gite037110f11e70
- Update to latest snapshot.

* Sat Jul 16 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.6.20110710git51d7d60a96d06
- Don't build java subpackage on ppc64, no java-1.6.0-devel package.

* Sun Jul 10 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.5.20110710git51d7d60a96d06
- Update to latest snapshot.

* Sat May 14 2011 Xavier Bachelot <xavier@bachelot.org> 0.2-0.4.20110514git46ee2766038e9
- Update to latest snapshot.
- Drop -static subpackage.

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-0.3.20110126gitbbf11e43bd82e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

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
