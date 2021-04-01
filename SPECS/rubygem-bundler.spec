%define namesuffix 25
%define rubysuffix 2.5
%define gemdir %(/usr/bin/ruby%{rubysuffix} -e 'puts Gem.respond_to?(:default_dirs) && Gem.default_dirs[:system] && Gem.default_dirs[:system][:gem_dir] || Gem::dir' 2>/dev/null)
%define gemname bundler
%define geminstdir %{gemdir}/gems/%{gemname}-%{version}

Summary: Bundler gem
Name: rubygem%{namesuffix}-%{gemname}

Version: 2.2.12
Release: 1%{?dist}
Group: Development/Libraries
License: MIT
URL: http://gembundler.com
Source: https://rubygems.org/downloads/bundler-%{version}.gem
Requires: rubygems%{namesuffix}
BuildRequires: sed
BuildRequires: rubygems%{namesuffix}
BuildRequires: rubygem%{namesuffix}-rdoc
BuildArch: noarch
Provides: %{gemname} = %{version}-%{release}
Provides: rubygem(%{gemname}) = %{version}-%{release}
Provides: rubygem-%{gemname} = %{version}-%{release}

%description
Bundler maintains a consistent environment for ruby applications. It tracks an application's code and the rubygems it needs to run, so that an application will always have the exact gems (and versions) that it needs to run.

%prep
%setup -c -T

%build
mkdir -p .%{gemdir}
echo %{gemdir}
gem%{rubysuffix} install -V --local --install-dir "`pwd`/%{gemdir}" --force --rdoc %{SOURCE0}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{gemdir}
cp -dpR .%{gemdir}/* %{buildroot}%{gemdir}/
for f in .gitignore .rspec .travis.yml .codeclimate.yml .rubocop_todo.yml .rubocop.yml bundler.gemspec; do
    rm -f "%{buildroot}%{geminstdir}/$f"
done

find %{buildroot}%{geminstdir}/exe -type f | xargs -n 1 sed -i -e 's"^#!/usr/bin/env ruby"#!%{_bindir}/ruby%{rubysuffix}"'

mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}%{gemdir}/bin/* %{buildroot}%{_bindir}
find %{buildroot}%{_bindir} -type f | xargs -n 1 sed -i -e 's"^#!/usr/bin/env ruby"#!%{_bindir}/ruby%{rubysuffix}"'
rmdir %{buildroot}%{gemdir}/bin

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root, -)
%{_bindir}/bundle
%{_bindir}/bundler
%dir %{geminstdir}
%{geminstdir}/lib
%{geminstdir}/exe
%doc %{geminstdir}/*.md
%{gemdir}/cache/%{gemname}-%{version}.gem
%{gemdir}/specifications/%{gemname}-%{version}.gemspec

%changelog
