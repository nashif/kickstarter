Summary:	Create kickstart files for meego images
Name:		kickstarter
Version:	0.14
Release:	1
License:	GPLv2
Group:		System/Base
URL:		http://www.meego.com
Source:		%{name}-%{version}.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:	noarch
Requires:   PyYAML
Requires:   python-urlgrabber
Requires:   python-cheetah
BuildRequires:  python-devel
BuildRequires:  python-cheetah

%description
Create Configuration files to build meego images

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL 

