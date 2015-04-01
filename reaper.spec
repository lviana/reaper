
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:		reaper
Version:	1.4
Release:	1%{?dist}
Summary:	Resource controller

License:	Apache
URL:		http://github.com/lviana/reaper
Source0:	reaper-%{version}.tar.bz2

BuildRequires:	python, python-devel, python-setuptools
Requires:	python, libcgroup, PyYAML, daemon


%description
Reaper is a resource controller for shared hosting environments, it
supports both native implementations of application servers or
Cpanel based shared hosting infrastructure.
It is easy to be extended or adapted to run on other platforms.


%prep
%setup -q -n reaper


%build
%{__python} setup.py build


%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%{__install} -D -m 0755 scripts/reaper.init $RPM_BUILD_ROOT%{_initrddir}/reaperd


%files
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/reaper.cfg
%attr(0755,root,root) %{_bindir}/reaperd
%attr(0750,root,root) %{_bindir}/reaper
%attr(0755,root,root) %{_initrddir}/reaperd
%defattr(0644,root,root,-)
%{python_sitelib}/reaper-0.1.0-py2.6.egg-info/PKG-INFO
%{python_sitelib}/reaper-0.1.0-py2.6.egg-info/SOURCES.txt
%{python_sitelib}/reaper-0.1.0-py2.6.egg-info/dependency_links.txt
%{python_sitelib}/reaper-0.1.0-py2.6.egg-info/top_level.txt
%{python_sitelib}/reaper/cgroups.py*
%{python_sitelib}/reaper/collectors.py*
%{python_sitelib}/reaper/__init__.py*


%changelog
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
