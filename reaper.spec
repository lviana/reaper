%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           reaper
Version:        1.5.1
Release:        1%{?dist}
Summary:        Shared resources controller

License:        Apache
URL:            http://github.com/lviana/reaper
Source0:        reaper-%{version}.tar.bz2

%if 0%{?fedora} < 17 && 0%{?rhel} < 7
Requires (post): chkconfig
%else
Requires (post): systemd
%endif
BuildRequires:  python, python-devel, python-setuptools
Requires:       python, libcgroup, PyYAML, daemon

%description
Reaper is a resource controller for shared hosting environments, it
supports both native implementations of application servers or
Cpanel based shared hosting infrastructure.
It is easy to be extended or adapted to run on other platforms.

%prep
%setup -q -n reaper

%build
%{__python} setup.py build

%pre
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
if [ -e "/etc/init.d/reaperd" ]; then
    /usr/sbin/service reaperd stop
fi
%else
if [ -e "/usr/lib/systemd/system/reaperd.service" ]; then
    /usr/bin/systemctl stop reaperd
fi
%endif

%preun
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
#Check if it is an uninstall or an upgrade
if [ $1 -eq 0 ]; then
    #package removal
    /sbin/chkconfig --del reaperd
fi
%else
/usr/bin/systemctl disable reaperd
%endif

%post
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
/sbin/chkconfig --add reaperd
/etc/init.d/reaperd restart
%else
/usr/bin/systemctl enable reaperd
/usr/bin/systemctl start reaperd
%endif

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
%{__install} -D -m 0755 scripts/reaper.init $RPM_BUILD_ROOT%{_initrddir}/reaperd
%else
%{__install} -d -m 0755 $RPM_BUILD_ROOT/usr/lib/systemd/system/
%{__install} -D -m 0755 -v scripts/reaperd.service $RPM_BUILD_ROOT/usr/lib/systemd/system/
%endif

%files
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/reaper.cfg
%attr(0755,root,root) %{_bindir}/reaperd
%attr(0750,root,root) %{_bindir}/reaper
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
%{python_sitelib}/reaper-%{version}-py2.6.egg-info
%attr(0755,root,root) %{_initrddir}/reaperd
%else
%{python_sitelib}/reaper-%{version}-py2.7.egg-info
%attr(0755,root,root) /usr/lib/systemd/system/reaperd.service
%endif
%defattr(0644,root,root,-)
%{python_sitelib}/reaper/cgroups.py*
%{python_sitelib}/reaper/__init__.py*
%{python_sitelib}/reaper/collectors/*


%changelog
* Mon Apr 06 2015 Luiz Viana <lviana@include.io> - 1.4.1-1
- CPU accounting ratio enabled on command line output

* Wed Apr 01 2015 Luiz Viana <lviana@include.io> - 1.4-1
- CPU accounting enabled on all groups
- Removed group prefix (g_)

* Thu Feb 26 2015 Luiz Viana <lviana@include.io> - 1.3-1
- Processor usage reporting enabled

* Tue Feb 24 2015 Luiz Viana <lviana@include.io> - 1.2-1
- Command line monitoring tool enabled

* Wed Feb 18 2015 Luiz Viana <lviana@include.io> - 1.1-1
- Added Plesk support
- Debian compatibility added on functions

* Tue Sep  9 2014 Luiz Viana <lviana@include.io> - 1.0-1
- Initial release
