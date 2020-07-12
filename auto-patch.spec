Name:		auto-patch
Version:	$version
Release:	0
Url:		$url
Summary:	$description
License:	Apache-2.0
Group:		System/Management
Source:		%{name}-%{version}.tar.gz
BuildRequires:	python3-base >= 3.4
Requires:	zypper
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


%files
%defattr(-,root,root)
%doc README.rst
%license LICENSE.txt
%exclude %{python3_sitelib}/*
%{_sbindir}/auto-patch


%changelog
