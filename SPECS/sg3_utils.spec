%global rescan_script rescan-scsi-bus.sh
%global _udevlibdir %{_prefix}/lib/udev

Summary: Utilities for devices that use SCSI command sets
Name:    sg3_utils
Version: 1.47
Release: 9%{?dist}
License: GPLv2+ and BSD
URL:     https://sg.danny.cz/sg/sg3_utils.html
Source0: https://sg.danny.cz/sg/p/sg3_utils-%{version}.tar.xz
Source2: scsi-rescan.8

# https://bugzilla.redhat.com/show_bug.cgi?id=2044433
# Covscan fixes
Patch0:  sg3_utils-1.48-initialize_sense_buffers.patch
Patch1:  sg3_utils-1.48-covscan_fixes.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2036718
# sg_readcap man page contains duplicate -R options
Patch2:  sg_readcap-man.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2035382
# rescan-scsi-bus.sh output shows tab (\t) and newline (\n) characters in output
Patch3:  rescan-scsi-bus_printf.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2036005
# https://bugzilla.redhat.com/show_bug.cgi?id=2035362
# rescan-scsi-bus.sh with "-r" switch deletes all scsi devices, especially boot disk which causes the system to hang
Patch4:  rescan-scsi-bus_sg_inq-parse.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2052512
# rescan-scsi-bus.sh: Fix scanning progress output
Patch5:  sg3_utils-1.48-rescan-scsi-bus.sh_seq_-s.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2073146
# missing new line in sg_vpd output
Patch6:  sg3_utils-1.48-sg_vpd_vendor-Fix-missing-newline-in-the-svpd_decode.patch

Requires: %{name}-libs%{?_isa} = %{version}-%{release}
BuildRequires: make
BuildRequires: gcc
BuildRequires: systemd

BuildRequires: gettext-devel
BuildRequires: automake
BuildRequires: autoconf
BuildRequires: libtool


%description
Collection of Linux utilities for devices that use the SCSI command set.
Includes utilities to copy data based on "dd" syntax and semantics (called
sg_dd, sgp_dd and sgm_dd); check INQUIRY data and VPD pages (sg_inq); check
mode and log pages (sginfo, sg_modes and sg_logs); spin up and down
disks (sg_start); do self tests (sg_senddiag); and various other functions.
See the README, CHANGELOG and COVERAGE files. Requires the linux kernel 2.4
series or later. In the 2.4 series SCSI generic device names (e.g. /dev/sg0)
must be used. In the 2.6 series other device names may be used as
well (e.g. /dev/sda).

Warning: Some of these tools access the internals of your system
and the incorrect usage of them may render your system inoperable.

%package libs
Summary: Shared library for %{name}

%description libs
This package contains the shared library for %{name}.

%package devel
Summary: Development library and header files for the sg3_utils library
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains the %{name} library and its header files for
developing applications.

%prep
%autosetup -p 1 -n sg3_utils-%{version}

%build
./autogen.sh
%configure --disable-static

# Don't use rpath!
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%make_build


%install
%make_install
rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.la

install -p -m 755 scripts/%{rescan_script} $RPM_BUILD_ROOT%{_bindir}
( cd $RPM_BUILD_ROOT%{_bindir}; ln -sf %{rescan_script} scsi-rescan )

install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_mandir}/man8

# install all extra udev rules
mkdir -p $RPM_BUILD_ROOT%{_udevrulesdir}
mkdir -p $RPM_BUILD_ROOT/usr/lib/udev
install -p -m 644 scripts/40-usb-blacklist.rules $RPM_BUILD_ROOT%{_udevrulesdir}
# need to run after 60-persistent-storage.rules
install -p -m 644 scripts/55-scsi-sg3_id.rules $RPM_BUILD_ROOT%{_udevrulesdir}/61-scsi-sg3_id.rules
# need to run after 62-multipath.rules
install -p -m 644 scripts/58-scsi-sg3_symlink.rules $RPM_BUILD_ROOT%{_udevrulesdir}/63-scsi-sg3_symlink.rules
install -p -m 644 scripts/59-scsi-cciss_id.rules $RPM_BUILD_ROOT%{_udevrulesdir}/65-scsi-cciss_id.rules
install -p -m 644 scripts/59-fc-wwpn-id.rules $RPM_BUILD_ROOT%{_udevrulesdir}/63-fc-wwpn-id.rules
install -p -m 755 scripts/fc_wwpn_id $RPM_BUILD_ROOT%{_udevlibdir}

%files
%doc AUTHORS BSD_LICENSE COPYING COVERAGE CREDITS ChangeLog README README.sg_start
%{_bindir}/*
%{_mandir}/man8/*
%{_udevrulesdir}/61-scsi-sg3_id.rules
%{_udevrulesdir}/63-scsi-sg3_symlink.rules
%{_udevrulesdir}/63-fc-wwpn-id.rules
%{_udevrulesdir}/65-scsi-cciss_id.rules
%{_udevrulesdir}/40-usb-blacklist.rules
%{_udevlibdir}/fc_wwpn_id

%files libs
%doc BSD_LICENSE COPYING
%{_libdir}/*.so.*

%files devel
%{_includedir}/scsi/*.h
%{_libdir}/*.so


%changelog
* Wed Jun 15 2022 Tomas Bzatek <tbzatek@redhat.com> - 1.47-9
- Fix missing newline in sg_vpd output (#2073146)

* Fri Feb 11 2022 Tomas Bzatek <tbzatek@redhat.com> - 1.47-8
- Fix scanning progress output (#2052512)

* Thu Jan 27 2022 Tomas Bzatek <tbzatek@redhat.com> - 1.47-7
- Fix sg_inq parsing in rescan-scsi-bus.sh (#2036005,#2035362)
- Fix rescan-scsi-bus.sh summary print (#2035382)
- sg_readcap --zbc man page switch fix (#2036718)
- Various Covscan fixes (#2044433)

* Mon Nov 15 2021 Tomas Bzatek <tbzatek@redhat.com> - 1.47-6
- update to stable version 1.47 (svn: r919) (#2011810)

* Wed Aug 18 2021 Tomas Bzatek <tbzatek@redhat.com> - 1.47-5
- update to pre-release version 1.47 (svn: r908) (#1971681)

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 1.47-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jun 15 2021 Tomas Bzatek <tbzatek@redhat.com> - 1.47-3
- update to pre-release version 1.47 (svn: r904) (#1970981)

* Thu May 27 2021 Tomas Bzatek <tbzatek@redhat.com> - 1.47-2
- Rebuild (#1963799)

* Mon May 17 2021 Tomas Bzatek <tbzatek@redhat.com> - 1.47-1
- update to pre-release version 1.47 (svn: r900)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.45-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.45-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.45-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 14 2020 Tom Stellard <tstellar@redhat.com> - 1.45-2
- Use make macros
- https://fedoraproject.org/wiki/Changes/UseMakeBuildInstallMacro

* Thu Mar 12 2020 Dan Horák <dan@danny.cz> - 1.45-1
- update to version 1.45 (#1809392)

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.44-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 06 2020 Tomas Bzatek <tbzatek@redhat.com> - 1.44-2
- Backport "rescan-scsi-bus.sh: use LUN wildcard in idlist"

* Fri Jan 03 2020 Tomas Bzatek <tbzatek@redhat.com> - 1.44-1
- Rebase to 1.44 release
- Enable supplemental udev rules
- Fix sg_turs help invocation in an old mode (#1683343)
- Fix sg_raw printing error about device not specified on version request (#1627657)
- Fix coverity scan warnings (#1633235)

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jul 16 2018 Dan Horák <dan[at]danny.cz> - 1.42-6
- fix build with new glibc - use sysmacros.h for major()/minor()

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.42-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Feb 21 2017 Than Ngo <than@redhat.com> - 1.42-1
- bz#1306078, update to 1.42
- bz#1230493, dropped Requires glibc-headers

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.41-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.41-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jul 08 2015 David Sommerseth <davids@redhat.com> - 1.41-1
- updated to version 1.41
- Corrected day/date mismatches in the changelog

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.40-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Dec 06 2014 Dan Horák <dan@danny.cz> - 1.40-1
- update to version 1.40 (#1164172)

* Wed Sep 03 2014 Dan Horák <dan@danny.cz> - 1.39-1
- update to version 1.39 (#1111893)

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.38-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.38-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 18 2014 Dan Horák <dan@danny.cz> - 1.38-1
- update to version 1.38 (#1083995)
- rebuild configure for ppc64le (#1079542)

* Wed Jan 29 2014 Dan Horák <dan@danny.cz> - 1.37-3
- fix various man pages (#948463)
- add man page for the rescan-scsi-bus.sh script

* Fri Oct 18 2013 Dan Horák <dan@danny.cz> - 1.37-2
- include fix for #920687

* Wed Oct 16 2013 Dan Horák <dan@danny.cz> - 1.37-1
- update to version 1.37
- switch to included rescan-scsi-bus script

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.36-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jun 06 2013 Dan Horák <dan@danny.cz> - 1.36-1
- update to version 1.36
- modernize spec

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.35-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 21 2013 Dan Horák <dan@danny.cz> - 1.35-1
- update to version 1.35

* Thu Oct 18 2012 Dan Horák <dan@danny.cz> - 1.34-1
- update to version 1.34

* Fri Sep 14 2012 Dan Horák <dan@danny.cz> - 1.33-4
- add fix for sg3_utils >= 1.32 to the rescan-scsi-bus script

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.33-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr  4 2012 Dan Horák <dan@danny.cz> - 1.33-2
- include rescan-scsi-bus script 1.56

* Tue Apr  3 2012 Dan Horák <dan@danny.cz> - 1.33-1
- update to version 1.33

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.31-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Feb 18 2011 Dan Horák <dan@danny.cz> - 1.31-1
- update to version 1.31

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.29-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jul  8 2010 Dan Horák <dan@danny.cz> - 1.29-2
- added license texts into -libs subpackage

* Mon Apr 12 2010 Dan Horák <dan@danny.cz> - 1.29-1
- update to version 1.29

* Thu Jan 14 2010 Dan Horák <dan@danny.cz> - 1.28-2
- include rescan-scsi-bus script 1.35
- rebase patches and add fix for issue mentioned in #538787

* Thu Oct 22 2009 Dan Horák <dan@danny.cz> - 1.28-1
- update to version 1.28
- added fixes from RHEL to rescan-scsi-bus.sh
- added scsi-rescan symlink to the rescan-scsi-bus.sh script

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.27-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 28 2009 Dan Horák <dan@danny.cz> - 1.27-1
- update to version 1.27
- changelog: http://sg.danny.cz/sg/p/sg3_utils.ChangeLog

* Tue Mar 31 2009 Dan Horák <dan@danny.cz> - 1.26-4
- add dependency between the libs subpackage and the main package (#492921)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.26-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Nov  3 2008 Dan Horák <dan@danny.cz> - 1.26-2
- update URL
- include rescan-scsi-bus script 1.29

* Mon Jun 30 2008 Dan Horák <dan@danny.cz> - 1.26-1
- update to upstream version 1.26

* Fri Mar 28 2008 Phil Knirsch <pknirsch@redhat.com> - 1.25-4
- Dropped really unnecessary Provides of sg_utils (#226414)
- Use --disable-static in configure (#226414)

* Thu Mar 27 2008 Phil Knirsch <pknirsch@redhat.com> - 1.25-3
- Specfile cleanup, removal of static development libraries (#226414)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.25-2
- Autorebuild for GCC 4.3

* Mon Oct 22 2007 Phil Knirsch <pknirsch@redhat.com> - 1.25-1
- Fixed URLs
- Updated to sg3_utils-1.25

* Thu Aug 16 2007 Phil Knirsch <pknirsch@redhat.com> - 1.23-2
- License review and update

* Fri Feb 02 2007 Phil Knirsch <pknirsch@redhat.com> - 1.23-1
- Update to sg3_utils-1.23
- Updated summary

* Mon Nov 13 2006 Phil Knirsch <pknirsch@redhat.com> - 1.22-1
- Update to sg3_utils-1.22

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.20-2.1
- rebuild

* Wed Jun 07 2006 Phil Knirsch <pknirsch@redhat.com> - 1.20-2
- Fixed rebuild problem on latest toolchain
- Added missing buildprereqs

* Fri May 19 2006 Phil Knirsch <pknirsch@redhat.com> - 1.20-1
- Update to sg3_utils-1.20.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.19-1.1
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Phil Knirsch <pknirsch@redhat.com> - 1.19-1
- Update to sg3_utils-1.19.
- Fixed rebuild problem on 64bit archs.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.17-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Nov 07 2005 Phil Knirsch <pknirsch@redhat.com> 1.17-1
- Update to sg3-utils-1.17
- Split package up into 3 subpackages: sg3_utils, devel and libs
- Some minor updates to the specfile

* Wed Mar 02 2005 Phil Knirsch <pknirsch@redhat.com> 1.06-5
- bump release and rebuild with gcc 4

* Fri Feb 18 2005 Phil Knirsch <pknirsch@redhat.com> 1.06-4
- rebuilt

* Tue Aug 03 2004 Phil Knirsch <pknirsch@redhat.com> 1.06-3
- rebuilt

* Thu Mar 11 2004 Tim Powers <timp@redhat.com> 1.06-2
- rebuild

* Wed Feb 18 2004 Phil Knirsch <pknirsch@redhat.com> 1.06-1
- Initial version for RHEL3 U2.

* Fri Jan 09 2004 - dgilbert@interlog.com
- sg3_utils.spec for mandrake; more sginfo work, sg_scan, sg_logs
  * sg3_utils-1.06

* Wed Nov 12 2003 - dgilbert@interlog.com
- sg_readcap: sizes; sg_logs: double fetch; sg_map 256 sg devices; sginfo
  * sg3_utils-1.05

* Tue May 13 2003 - dgilbert@interlog.com
- default sg_turs '-n=' to 1, sg_logs gets '-t' for temperature, CREDITS
  * sg3_utils-1.04

* Wed Apr 02 2003 - dgilbert@interlog.com
- 6 byte CDBs for sg_modes, sg_start on block devs, sg_senddiag, man pages
  * sg3_utils-1.03

* Wed Jan 01 2003 - dgilbert@interlog.com
- interwork with block SG_IO, fix in sginfo, '-t' for sg_turs
  * sg3_utils-1.02

* Wed Aug 14 2002 - dgilbert@interlog.com
- raw switch in sg_inq
  * sg3_utils-1.01

* Sun Jul 28 2002 - dgilbert@interlog.com
- decode sg_logs pages, add dio to sgm_dd, drop "gen=1" arg, "of=/dev/null"
  * sg3_utils-1.00

* Sun Mar 17 2002 - dgilbert@interlog.com
- add sg_modes+sg_logs for sense pages, expand sg_inq, add fua+sync to sg_dd++
  * sg3_utils-0.99

* Sat Feb 16 2002 - dgilbert@interlog.com
- resurrect sg_reset; snprintf cleanup, time,gen+cdbsz args to sg_dd++
  * sg3_utils-0.98

* Sun Dec 23 2001 - dgilbert@interlog.com
- move isosize to archive directory; now found in util-linux-2.10s and later
  * sg3_utils-0.97

* Fri Dec 21 2001 - dgilbert@interlog.com
- add sgm_dd, sg_read, sg_simple4 and sg_simple16 [add mmap-ed IO support]
  * sg3_utils-0.96

* Sat Sep 15 2001 - dgilbert@interlog.com
- sg_map can do inquiry; sg_dd, sgp_dd + sgq_dd dio help
  * sg3_utils-0.95

* Thu Apr 19 2001 - dgilbert@interlog.com
- add sg_start, improve sginfo and sg_map [Kurt Garloff]
  * sg3_utils-0.94

* Mon Mar 5 2001 - dgilbert@interlog.com
- add scsi_devfs_scan, add sg_include.h, 'coe' more general in sgp_dd
  * sg3_utils-0.93

* Tue Jan 16 2001 - dgilbert@interlog.com
- clean sg_err.h include dependencies, bug fixes, Makefile in archive directory
  * sg3_utils-0.92

* Thu Dec 21 2000 - dgilbert@interlog.com
- signals for sg_dd, man pages and additions for sg_rbuf and isosize
  * sg3_utils-0.91

* Mon Dec 11 2000 - dgilbert@interlog.com
- Initial creation of package, containing
  * sg3_utils-0.90
