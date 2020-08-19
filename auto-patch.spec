Name:		auto-patch
Version:	$version
Release:	0
Url:		$url
Summary:	$description
License:	Apache-2.0
Group:		System/Management
Source:		%{name}-%{version}.tar.gz
BuildRequires:	python3-base >= 3.5
BuildRequires:	systemd-rpm-macros
Requires:	lsof
Requires:	systemd
Requires:	zypper
%systemd_requires
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

%description
$long_description


%prep
%setup -q


%build
python3 setup.py build


%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot} --install-scripts=%{_sbindir}
mv %{buildroot}%{_sbindir}/auto-patch.py %{buildroot}%{_sbindir}/auto-patch
install -d -m 755 %{buildroot}%{_unitdir}
cp -p systemd/* %{buildroot}%{_unitdir}


%pre
%service_add_pre %{name}.timer

%post
%service_add_post %{name}.timer

%preun
%service_del_preun %{name}.timer

%postun
%service_del_postun %{name}.timer


%files
%defattr(-,root,root)
%doc README.rst CHANGES.rst
%license LICENSE.txt
%exclude %{python3_sitelib}/*
%{_sbindir}/auto-patch
%{_unitdir}/*


%changelog
