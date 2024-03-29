%define _buildid .2

%bcond_with X11
%bcond_with doc_capi # without

# If we are also building an independent gem, don't produce a gem subpackage
%bcond_without rake_package
%bcond_without json_package
%bcond_without minitest_package
%bcond_without power_assert_package
%bcond_without rdoc_package

# We don't currently package these separately
%bcond_without rubygems_package # with
%bcond_without did_you_mean_package # with

%global major_version 2
%global minor_version 5
%global teeny_version 9

# Ruby 2.0 is the default version in AL, at priority 2000.
%global priority 243

%global major_minor_version %{major_version}.%{minor_version}

%global ruby_version %{major_minor_version}.%{teeny_version}
%global ruby_release %{ruby_version}
%global base_ver %{major_version}%{minor_version}

%global ruby_archive ruby-%{ruby_version}

# Do NOT decrement this variable! ruby contains a number of subpackages which have specific versions
# that differ from the main Ruby release that may not increment when the main Ruby package is upgraded
# Decrementing this number may cause some subpackages to have a lower NVR then the previous version
%global release 1

# Bundled libraries versions
%global rubygems_version 2.7.6.3
%global molinillo_version 0.5.7

# TODO: The IRB has strange versioning. Keep the Ruby's versioning ATM.
# http://redmine.ruby-lang.org/issues/5313
%global irb_version %{ruby_version}

%global bigdecimal_version 1.3.4
%global did_you_mean_version 1.2.0
%global io_console_version 0.4.6
%global json_version 2.1.0
%global minitest_version 5.10.3
%global openssl_version 2.1.2
%global power_assert_version 1.1.1
%global psych_version 3.0.2
%global rake_version 12.3.3
%global rdoc_version 6.0.1.1
%global xmlrpc_version 0.3.0

# Might not be needed in the future, if we are lucky enough.
# https://bugzilla.redhat.com/show_bug.cgi?id=888262
%global tapset_root %{_datadir}/systemtap
%global tapset_dir %{tapset_root}/tapset
%global tapset_libdir %(echo %{_libdir} | sed 's/64//')*

%global _normalized_cpu %(echo %{_target_cpu} | sed 's/^ppc/powerpc/;s/i.86/i386/;s/sparcv./sparc/')

Summary: An interpreter of object-oriented scripting language
Name: ruby%{base_ver}
Version: %{ruby_version}
Release: %{release}.0%{?_buildid}%{?dist}
Group: Development/Languages
# Public Domain for example for: include/ruby/st.h, strftime.c, missing/*, ...
# MIT and CCO: ccan/*
# zlib: ext/digest/md5/md5.*, ext/nkf/nkf-utf8/nkf.c
# UCD: some of enc/trans/**/*.src
License: (Ruby or BSD) and Public Domain and MIT and CC0 and zlib and UCD
URL: http://ruby-lang.org/
Source0: https://cache.ruby-lang.org/pub/ruby/%{major_minor_version}/%{ruby_archive}.tar.xz
Source1: operating_system.rb
# TODO: Try to push SystemTap support upstream.
Source2: libruby.stp
Source3: ruby-exercise.stp
Source4: macros.ruby
Source5: macros.rubygems
# This wrapper fixes https://bugzilla.redhat.com/show_bug.cgi?id=977941
# Hopefully, it will get removed soon:
# https://fedorahosted.org/fpc/ticket/312
# https://bugzilla.redhat.com/show_bug.cgi?id=977941
Source7: config.h
# SystemTap tests.
Source13: test_systemtap.rb


# Include the constants defined in macros files.
# http://rpm.org/ticket/866
%{lua:

function source_macros(file)
  local macro = nil

  for line in io.lines(file) do
    if not macro and line:match("^%%") then
      macro = line:match("^%%(.*)$")
      line = nil
    end

    if macro then
      if line and macro:match("^.-%s*\\%s*$") then
        macro = macro .. '\n' .. line
      end

      if not macro:match("^.-%s*\\%s*$") then
        rpm.define(macro)
        macro = nil
      end
    end
  end
end

source_macros(rpm.expand("%{SOURCE4}"))
source_macros(rpm.expand("%{SOURCE5}"))

}

%global ruby_libdir %ruby25_libdir
%global ruby_libarchdir %ruby25_libarchdir
%global ruby_libdir_parent %ruby25_libdir_parent
%global ruby_libarchdir_parent %ruby25_libarchdir_parent
%global ruby_sitearchdir %ruby25_sitearchdir
%global ruby_hdrdir %ruby25_hdrdir
%global ruby_sitelibdir %ruby25_sitelibdir
%global ruby_sitelibdir_parent %ruby25_sitelibdir_parent
%global ruby_sitehdrdir %ruby25_sitehdrdir
%global ruby_vendorlibdir %ruby25_vendorlibdir
%global ruby_vendorlibdir_parent %ruby25_vendorlibdir_parent
%global ruby_vendorarchdir %ruby25_vendorarchdir
%global ruby_vendorhdrdir %ruby25_vendorhdrdir
%global gem_dir %gem25_dir
%global gem_archdir %gem25_archdir

# Fix ruby_version abuse.
# http://bugs.ruby-lang.org/issues/7807
Patch1: ruby-2.2.0-Prevent-dupe-paths-when-empty-version-string-configured.patch
# Allows to override libruby.so placement. Hopefully we will be able to return
# to plain --with-rubyarchprefix.
# http://bugs.ruby-lang.org/issues/8973
Patch2: ruby-2.1.0-Enable-configuration-of-archlibdir.patch
# Force multiarch directories for i.86 to be always named i386. This solves
# some differencies in build between Fedora and RHEL.
Patch3: ruby-2.1.0-always-use-i386.patch
# Allows to install RubyGems into custom directory, outside of Ruby's tree.
# http://bugs.ruby-lang.org/issues/5617
Patch4: ruby-2.1.0-custom-rubygems-location.patch
# Make mkmf verbose by default
Patch5: ruby-1.9.3-mkmf-verbose.patch
# Adds support for '--with-prelude' configuration option. This allows to built
# in support for ABRT.
# http://bugs.ruby-lang.org/issues/8566
### Patch6: ruby-2.1.0-Allow-to-specify-additional-preludes-by-configuratio.patch
# Use miniruby to regenerate prelude.c.
# https://bugs.ruby-lang.org/issues/10554
Patch7: ruby-2.2.3-Generate-preludes-using-miniruby.patch
# Workaround "an invalid stdio handle" error on PPC, due to recently introduced
# hardening features of glibc (rhbz#1361037).
# https://bugs.ruby-lang.org/issues/12666
Patch9: ruby-2.3.1-Rely-on-ldd-to-detect-glibc.patch
# CVE-2019-8320: Directory traversal using symlink when decompressing tar
# CVE-2019-8321: Escape sequence injection vulnerability in verbose
# https://bugzilla.redhat.com/show_bug.cgi?id=1692514
# CVE-2019-8322: Escape sequence injection vulnerability in gem owner
# https://bugzilla.redhat.com/show_bug.cgi?id=1692516
# CVE-2019-8323: Escape sequence injection vulnerability in API response handling
# https://bugzilla.redhat.com/show_bug.cgi?id=1692519
# CVE-2019-8324: Installing a malicious gem may lead to arbitrary code execution
# https://bugzilla.redhat.com/show_bug.cgi?id=1692520
# CVE-2019-8325: Escape sequence injection vulnerability in errors
# https://bugzilla.redhat.com/show_bug.cgi?id=1692522
# https://github.com/ruby/ruby/commit/f86e5daee790ee509cb17f4f51f95cc76ca89a4e
### Patch10: ruby-2.4.6-Applied-security-patches-for-RubyGems.patch
### Patch11: ruby-2.6.0-Update-for-tzdata-2018f.patch

# Amazon Patches
Patch100: ruby-2.2.0-arch-path-fix.patch
Patch101: ruby-2.2.3-test-new-glibc.patch
Patch102: ruby-2.0.0-skip-test-with-external-ruby.patch
Patch103: ruby-2.4.1-remove-win32-tests.patch
Patch104: ruby-2.4.1-disable-rinda-multicast-checks.patch
### Patch105: 0001-Update-net-test-SSL-key-cert-fixture.patch
Patch106: 0001-gem-install-test-fix.patch

# Custom Patches
Patch900: ruby-2.5.9-fix-test-https-get.patch
Patch901: ruby-2.5.9-decode-only-cookie-values.patch
Patch902: ruby-2.5.9-limit-length-of-date-strings.patch

Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: ruby%{base_ver}(rubygems) >= %{rubygems_version}
# Make the bigdecimal gem a runtime dependency of Ruby to avoid problems
# with user-installed gems, that don't require it in gemspec/Gemfile
# See https://bugzilla.redhat.com/show_bug.cgi?id=829209
# and http://bugs.ruby-lang.org/issues/6123
Requires: rubygem%{base_ver}(bigdecimal) >= %{bigdecimal_version}
# Many gems from rubygems.org assume that because these gems are shipped with
# the main Ruby package they are always availible and don't include them in
# the gems requirement list. Always require these so user-installed gems
# that make this assumption always work
Requires: rubygem%{base_ver}(json)       >= %{json_version}
Requires: rubygem%{base_ver}(psych)      >= %{psych_version}

Requires(post): %{_sbindir}/update-alternatives
Requires(preun): %{_sbindir}/update-alternatives

BuildRequires: autoconf
%if %{with doc_capi}
BuildRequires: doxygen
%endif
BuildRequires: gdbm-devel
BuildRequires: ncurses-devel
%if 0%{?fedora} >= 18 || 0%{?__have_libdb}
BuildRequires: libdb-devel
%else
BuildRequires: db4-devel
%endif
BuildRequires: libffi-devel
BuildRequires: openssl-devel
BuildRequires: libyaml-devel
BuildRequires: readline-devel
%if %{with X11}
BuildRequires: tk-devel
%endif
# Needed to pass test_set_program_name(TestRubyOptions)
BuildRequires: procps
BuildRequires: %{_bindir}/dtrace
# RubyGems test suite optional dependencies.
BuildRequires: %{_bindir}/git
BuildRequires: %{_bindir}/cmake
# Unbundle cert.pem
BuildRequires: ca-certificates

Provides: ruby = %{version}-%{release}
Provides: ruby%{?_isa} = %{version}-%{release}
Provides: ruby(release) = %{ruby_release}
Provides: ruby(abi) = %{major_minor_version}

%global __provides_exclude_from ^(%{ruby_libarchdir}|%{gem_archdir}|%ruby_vendorarchdir})/.*\\.so$

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.


%package devel
Summary:    A Ruby development environment
Group:      Development/Languages
Requires:   %{name}%{?_isa} = %{version}-%{release}
Provides:   ruby-devel = %{version}-%{release}
Provides:   ruby-devel%{?_isa} = %{version}-%{release}

%description devel
Header files and libraries for building an extension library for the
Ruby or an application embedding Ruby.

%package libs
Summary:    Libraries necessary to run Ruby
Group:      Development/Libraries
License:    Ruby or BSD
# Requires power_assert for bundled test-unit.
Requires:   rubygem%{base_ver}(power_assert)
Provides:   ruby-libs = %{version}-%{release}
Provides:   ruby-libs%{?_isa} = %{version}-%{release}

# Virtual provides for CCAN copylibs.
# https://fedorahosted.org/fpc/ticket/364
Provides: bundled(ccan-build_assert)
Provides: bundled(ccan-check_type)
Provides: bundled(ccan-container_of)
Provides: bundled(ccan-list)

%description libs
This package includes the libruby, necessary to run Ruby.

%if %{with rubygems_package}
%package -n rubygems%{base_ver}
Summary:    The Ruby standard for packaging ruby libraries
Version:    %{rubygems_version}
Group:      Development/Libraries
License:    Ruby or MIT
Requires:   %{_bindir}/ruby%{major_minor_version}
# This rdoc requirement is unversioned because we package a lower version
# separately; the rdoc gem is different than the bundled version
# and has testing issues.
Requires:   rubygem%{base_ver}(rdoc)
Requires:   rubygem%{base_ver}(io-console) >= %{io_console_version}
Requires:   rubygem%{base_ver}(psych) >= %{psych_version}
Requires:   ca-certificates
Provides:   gem = %{rubygems_version}
Provides:   gem%{base_ver} = %{rubygems_version}
Provides:   ruby(rubygems) = %{rubygems_version}
Provides:   ruby%{base_ver}(rubygems) = %{rubygems_version}
Provides:   rubygems = %{rubygems_version}
# https://github.com/rubygems/rubygems/pull/1189#issuecomment-121600910
Provides:   bundled(rubygem(molinillo)) = %{molinillo_version}
Provides:   bundled(rubygem%{base_ver}(molinillo)) = %{molinillo_version}
Provides:   bundled(rubygem-molinillo) = %{molinillo_version}
BuildArch:  noarch

%description -n rubygems%{base_ver}
RubyGems is the Ruby standard for publishing and managing third party
libraries.


%package -n rubygems%{base_ver}-devel
Summary:    Macros and development tools for packaging RubyGems
Version:    %{rubygems_version}
Group:      Development/Libraries
License:    Ruby or MIT
Requires:   ruby%{base_ver}(rubygems) = %{rubygems_version}
# Needed for RDoc documentation format generation.
Requires:   rubygem%{base_ver}(json) >= %{json_version}
Requires:   rubygem%{base_ver}(rdoc) >= %{rdoc_version}
Provides:   rubygems-devel = %{rubygems_version}
BuildArch:  noarch

%description -n rubygems%{base_ver}-devel
Macros and development tools for packaging RubyGems.
%endif


%if %{with rake_package}
%package -n rubygem%{base_ver}-rake
Summary:    Ruby based make-like utility
Version:    %{rake_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rake = %{rake_version}
Provides:   rubygem(rake) = %{rake_version}
Provides:   rubygem%{base_ver}(rake) = %{rake_version}
Provides:   rubygem-rake = %{rake_version}
BuildArch:  noarch

%description -n rubygem%{base_ver}-rake
Rake is a Make-like program implemented in Ruby. Tasks and dependencies are
specified in standard Ruby syntax.
%endif


%package irb
Summary:    The Interactive Ruby
Version:    %{irb_version}
Group:      Development/Libraries
Requires:   %{name} = %{ruby_version}
Provides:   irb = %{irb_version}
Provides:   ruby(irb) = %{irb_version}
Provides:   ruby%{base_ver}(irb) = %{irb_version}
Provides:   ruby-irb = %{irb_version}
BuildArch:  noarch

%description irb
The irb is acronym for Interactive Ruby.  It evaluates ruby expression
from the terminal.


%if %{with rdoc_package}
%package -n rubygem%{base_ver}-rdoc
Summary:    A tool to generate HTML and command-line documentation for Ruby projects
Version:    %{rdoc_version}
Group:      Development/Libraries
# SIL-OFL: lib/rdoc/generator/template/darkfish/css/fonts.css
License:    GPLv2 and Ruby and MIT and OFL
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Requires:   ruby%{base_ver}(irb) = %{irb_version}
Requires:   rubygem%{base_ver}(json) >= %{json_version}
Provides:   rdoc = %{rdoc_version}
Provides:   ri = %{rdoc_version}
Provides:   ri%{base_ver} = %{rdoc_version}
Provides:   rubygem(rdoc) = %{rdoc_version}
Provides:   rubygem%{base_ver}(rdoc) = %{rdoc_version}
Provides:   rubygem-rdoc = %{rdoc_version}
BuildArch:  noarch

%description -n rubygem%{base_ver}-rdoc
RDoc produces HTML and command-line documentation for Ruby projects.  RDoc
includes the 'rdoc' and 'ri' tools for generating and displaying online
documentation.
%endif


%package doc
Summary:    Documentation for %{name}
Group:      Documentation
Requires:   %{_bindir}/ri%{major_minor_version}
Provides:   ruby-doc = %{version}-%{release}
BuildArch:  noarch

%description doc
This package contains documentation for %{name}.


%package -n rubygem%{base_ver}-bigdecimal
Summary:    BigDecimal provides arbitrary-precision floating point decimal arithmetic
Version:    %{bigdecimal_version}
Group:      Development/Libraries
License:    GPL+ or Artistic
Requires:   ruby(release) = %{ruby_release}
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(bigdecimal) = %{bigdecimal_version}
Provides:   rubygem%{base_ver}(bigdecimal) = %{bigdecimal_version}
Provides:   rubygem-bigdecimal = %{bigdecimal_version}
Provides:   rubygem-bigdecimal%{?_isa} = %{bigdecimal_version}

%description -n rubygem%{base_ver}-bigdecimal
Ruby provides built-in support for arbitrary precision integer arithmetic.
For example:

42**13 -> 1265437718438866624512

BigDecimal provides similar support for very large or very accurate floating
point numbers. Decimal arithmetic is also useful for general calculation,
because it provides the correct answers people expect–whereas normal binary
floating point arithmetic often introduces subtle errors because of the
conversion between base 10 and base 2.


%if %{with did_you_mean_package}
%package -n rubygem%{base_ver}-did_you_mean
Summary:    "Did you mean?" experience in Ruby
Version:    %{did_you_mean_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(did_you_mean) = %{did_you_mean_version}
Provides:   rubygem%{base_ver}(did_you_mean) = %{did_you_mean_version}
Provides:   rubygem-did_you_mean = %{did_you_mean_version}
BuildArch:  noarch

%description -n rubygem%{base_ver}-did_you_mean
"did you mean?" experience in Ruby: the error message will tell you the right
one when you misspelled something.
%endif


%package -n rubygem%{base_ver}-io-console
Summary:    IO/Console is a simple console utilizing library
Version:    %{io_console_version}
Group:      Development/Libraries
Requires:   ruby(release) = %{ruby_release}
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(io-console) = %{io_console_version}
Provides:   rubygem%{base_ver}(io-console) = %{io_console_version}
Provides:   rubygem-io-console = %{io_console_version}
Provides:   rubygem-io-console%{?_isa} = %{io_console_version}

%description -n rubygem%{base_ver}-io-console
IO/Console provides very simple and portable access to console. It doesn't
provide higher layer features, such like curses and readline.


%if %{with json_package}
%package -n rubygem%{base_ver}-json
Summary:    This is a JSON implementation as a Ruby extension in C
Version:    %{json_version}
Group:      Development/Libraries
# UCD: ext/json/generator/generator.c
License:    (Ruby or GPLv2) and UCD
Requires:   ruby(release) = %{ruby_release}
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(json) = %{json_version}
Provides:   rubygem%{base_ver}(json) = %{json_version}
Provides:   rubygem-json = %{json_version}
Provides:   rubygem-json%{?_isa} = %{json_version}

%description -n rubygem%{base_ver}-json
This is a implementation of the JSON specification according to RFC 4627.
You can think of it as a low fat alternative to XML, if you want to store
data to disk or transmit it over a network rather than use a verbose
markup language.
%endif


%if %{with minitest_package}
# minitest 5 is incompatible with prior versions; version the provides
%package -n rubygem%{base_ver}-minitest5
Summary:    Minitest provides a complete suite of testing facilities
Version:    %{minitest_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(minitest5) = %{minitest_version}
Provides:   rubygem%{base_ver}(minitest5) = %{minitest_version}
BuildArch:  noarch

%description -n rubygem%{base_ver}-minitest5
minitest/unit is a small and incredibly fast unit testing framework.

minitest/spec is a functionally complete spec engine.

minitest/benchmark is an awesome way to assert the performance of your
algorithms in a repeatable manner.

minitest/mock by Steven Baker, is a beautifully tiny mock object
framework.

minitest/pride shows pride in testing and adds coloring to your test
output.
%endif


%if %{with power_assert_package}
%package -n rubygem%{base_ver}-power_assert
Summary:    Power Assert for Ruby helps debug failing tests
Version:    %{power_assert_version}
Group:      Development/Libraries
License:    Ruby or BSD
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(power_assert) = %{power_assert_version}
Provides:   rubygem%{base_ver}(power_assert) = %{power_assert_version}
Provides:   rubygem-power_assert = %{power_assert_version}
BuildArch:  noarch

%description -n rubygem%{base_ver}-power_assert
Power Assert shows each value of variables and method calls in the expression.
It is useful for testing, providing which value wasn't correct when the
condition is not satisfied.
%endif


%package -n rubygem%{base_ver}-psych
Summary:    A libyaml wrapper for Ruby
Version:    %{psych_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby(release) = %{ruby_release}
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(psych) = %{psych_version}
Provides:   rubygem%{base_ver}(psych) = %{psych_version}
Provides:   rubygem-psych = %{psych_version}
Provides:   rubygem-psych%{?_isa} = %{psych_version}

%description -n rubygem%{base_ver}-psych
Psych is a YAML parser and emitter. Psych leverages
libyaml[http://pyyaml.org/wiki/LibYAML] for its YAML parsing and emitting
capabilities. In addition to wrapping libyaml, Psych also knows how to
serialize and de-serialize most Ruby objects to and from the YAML format.




%package -n rubygem%{base_ver}-xmlrpc
Summary:    XMLRPC is a lightweight protocol that enables remote procedure calls over HTTP
Version:    %{xmlrpc_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby(release) = %{ruby_release}
Requires:   ruby%{base_ver}(rubygems) >= %{rubygems_version}
Provides:   rubygem(xmlrpc) = %{xmlrpc_version}
Provides:   rubygem%{base_ver}(xmlrpc) = %{xmlrpc_version}
Provides:   rubygem-xmlrpc = %{xmlrpc_version}
Provides:   rubygem-xmlrpc%{?_isa} = %{xmlrpc_version}

%description -n rubygem%{base_ver}-xmlrpc
XMLRPC is a lightweight protocol that enables remote procedure calls over
HTTP.



%if %{with X11}
%package tcltk
Summary:    Tcl/Tk interface for scripting language Ruby
Group:      Development/Languages
Requires:   %{name}-libs%{?_isa} = %{ruby_version}
Provides:   ruby(tcltk) = %{ruby_version}-%{release}
Provides:   ruby%{base_ver}(tcltk) = %{ruby_version}-%{release}
Provides:   ruby-tcltk = %{ruby_version}-%{release}
Provides:   ruby-tcltk%{?_isa} = %{ruby_version}-%{release}

%description tcltk
Tcl/Tk interface for the object-oriented scripting language Ruby.
%endif

%prep
%setup -q -n %{ruby_archive}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
### %patch6 -p1
%patch7 -p1
%patch9 -p1
### %patch10 -p1
### %patch11 -p1

# Amazon patches
%patch100 -p1
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1
### %patch105 -p1
%patch106 -p1
%patch900 -p1
%patch901 -p1
%patch902 -p1

# Provide an example of usage of the tapset:
cp -a %{SOURCE3} .

%build
autoconf

%configure \
        --with-rubylibprefix='%{ruby_libdir_parent}' \
        --with-archlibdir='%{_libdir}' \
        --with-rubyarchprefix='%{ruby_libarchdir_parent}' \
        --with-sitedir='%{ruby_sitelibdir_parent}' \
        --with-sitearchdir='%{ruby_sitearchdir}' \
        --with-vendordir='%{ruby_vendorlibdir_parent}' \
        --with-vendorarchdir='%{ruby_vendorarchdir}' \
        --with-rubyhdrdir='%{ruby_hdrdir}' \
        --with-rubyarchhdrdir='$(rubyhdrdir)' \
        --with-sitearchhdrdir='$(sitehdrdir)' \
        --with-vendorarchhdrdir='$(rubyarchhdrdir)' \
        --with-rubygemsdir='%{ruby_vendorlibdir}' \
        --with-ruby-pc='ruby-%{major_minor_version}.pc' \
        --with-vendorhdrdir='$(rubyhdrdir)' \
        --with-sitehdrdir='%{ruby_sitehdrdir}' \
%if %{without doc_capi}
        --disable-install-capi \
%else
        --enable-install-capi \
%endif
        --disable-rpath \
        --enable-shared \
        --with-ruby-version='%{major_minor_version}' \
        --enable-multiarch \
%if %{without X11}
        --with-out-ext=tcl \
        --with-out-ext=tk \
%endif
        --program-suffix='%{major_minor_version}'


# Q= makes the build output more verbose and allows to check Fedora
# compiler options.
make %{?_smp_mflags} COPY="cp -p" Q=

%install
rm -rf %{buildroot}

mkdir -p ./lib/rubygems/defaults/
touch ./lib/rubygems/defaults/operating_system.rb
# Note: if ruby is already installed when this runs, it will install gems to
# ~/.gem instead of /usr (inside the buildroot) so packaging will fail.
make install DESTDIR=%{buildroot}

# Rename ruby/config.h to ruby/config-<arch>.h to avoid file conflicts on
# multilib systems and install config.h wrapper
mv %{buildroot}%{ruby_hdrdir}/ruby/config.h %{buildroot}%{ruby_hdrdir}/ruby/config-%{_arch}.h
install -m644 %{SOURCE7} %{buildroot}%{ruby_hdrdir}/ruby/config.h

# Version is empty if --with-ruby-version is specified.
# http://bugs.ruby-lang.org/issues/7807
sed -i 's/Version: \${ruby_version}/Version: %{ruby_version}/' %{buildroot}%{_libdir}/pkgconfig/ruby-%{major_minor_version}.pc

# Since we install libruby.so into a version specific directory we need to add the version specific directory to
# the cflags otherwise linking breaks
sed -i -r 's|^Libs: (.*)|Libs: \-L${rubyarchdir} \1|g' %{buildroot}%{_libdir}/pkgconfig/ruby-%{major_minor_version}.pc

# Kill bundled certificates, as they should be part of ca-certificates.
rm -rf %{buildroot}%{ruby_vendorlibdir}/rubygems/ssl_certs/*

# Kill bundled cert.pem
mkdir -p %{buildroot}%{ruby_vendorlibdir}/rubygems/ssl_certs/
ln -sf %{_sysconfdir}/pki/tls/cert.pem \
  %{buildroot}%{ruby_vendorlibdir}/rubygems/ssl_certs/ca-bundle.pem

# Move macros file into proper place and replace the %%{name} macro
mkdir -p %{buildroot}%{_sysconfdir}/rpm
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/rpm/macros.ruby%{base_ver}
install -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/rpm/macros.rubygems%{base_ver}

# Install custom operating_system.rb.
mkdir -p %{buildroot}%{ruby_vendorlibdir}/rubygems/defaults
cp %{SOURCE1} %{buildroot}%{ruby_vendorlibdir}/rubygems/defaults

mkdir -p %{buildroot}%{gem_dir}
mkdir -p %{buildroot}%{gem_archdir}

# Move bundled rubygems to %%gem_dir and %%gem_archdir
mkdir -p %{buildroot}%{gem_dir}/gems/rdoc-%{rdoc_version}/lib
mv %{buildroot}%{ruby_libdir}/rdoc* %{buildroot}%{gem_dir}/gems/rdoc-%{rdoc_version}/lib
mv %{buildroot}%{gem_dir}/specifications/default/rdoc-%{rdoc_version}.gemspec %{buildroot}%{gem_dir}/specifications
mv %{buildroot}%{gem_dir}/specifications/default/openssl-%{openssl_version}.gemspec %{buildroot}%{gem_dir}/specifications

# make symlinks for io-console and bigdecimal, which are considered to be part of stdlib by other Gems
mkdir -p %{buildroot}%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib
mkdir -p %{buildroot}%{gem_archdir}/gems/bigdecimal-%{bigdecimal_version}
mv %{buildroot}%{ruby_libdir}/bigdecimal %{buildroot}%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib
mv %{buildroot}%{ruby_libarchdir}/bigdecimal.so %{buildroot}%{gem_archdir}/gems/bigdecimal-%{bigdecimal_version}
mv %{buildroot}%{gem_dir}/specifications/default/bigdecimal-%{bigdecimal_version}.gemspec %{buildroot}%{gem_dir}/specifications
ln -s %{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib/bigdecimal %{buildroot}%{ruby_libdir}/bigdecimal
ln -s %{gem_archdir}/gems/bigdecimal-%{bigdecimal_version}/bigdecimal.so %{buildroot}%{ruby_libarchdir}/bigdecimal.so

mkdir -p %{buildroot}%{gem_dir}/gems/io-console-%{io_console_version}/lib
mkdir -p %{buildroot}%{gem_archdir}/gems/io-console-%{io_console_version}/io
mv %{buildroot}%{ruby_libdir}/io %{buildroot}%{gem_dir}/gems/io-console-%{io_console_version}/lib
mv %{buildroot}%{ruby_libarchdir}/io/console.so %{buildroot}%{gem_archdir}/gems/io-console-%{io_console_version}/io
mv %{buildroot}%{gem_dir}/specifications/default/io-console-%{io_console_version}.gemspec %{buildroot}%{gem_dir}/specifications
# Many gems still assume this is part of the Ruby base and don't list it as a dependency. Without these sym links
# many gems in a bundle environment break
ln -s %{gem_dir}/gems/io-console-%{io_console_version}/lib/io %{buildroot}%{ruby_libdir}/io
ln -s %{gem_archdir}/gems/io-console-%{io_console_version}/io/console.so %{buildroot}%{ruby_libarchdir}/io/console.so

mkdir -p %{buildroot}%{gem_dir}/gems/json-%{json_version}/lib
mkdir -p %{buildroot}%{gem_archdir}/gems/json-%{json_version}
mv %{buildroot}%{ruby_libdir}/json* %{buildroot}%{gem_dir}/gems/json-%{json_version}/lib
mv %{buildroot}%{ruby_libarchdir}/json/ %{buildroot}%{gem_archdir}/gems/json-%{json_version}/
mv %{buildroot}%{gem_dir}/specifications/default/json-%{json_version}.gemspec %{buildroot}%{gem_dir}/specifications

mkdir -p %{buildroot}%{gem_dir}/gems/psych-%{psych_version}/lib
mkdir -p %{buildroot}%{gem_archdir}/gems/psych-%{psych_version}
mv %{buildroot}%{ruby_libdir}/psych* %{buildroot}%{gem_dir}/gems/psych-%{psych_version}/lib
mv %{buildroot}%{ruby_libarchdir}/psych.so %{buildroot}%{gem_archdir}/gems/psych-%{psych_version}/
mv %{buildroot}%{gem_dir}/specifications/default/psych-%{psych_version}.gemspec %{buildroot}%{gem_dir}/specifications
# Many gems still assume this is part of the Ruby base and don't list it as a dependency. Without these sym links
# many gems in a bundle environment break
ln -s %{gem_dir}/gems/psych-%{psych_version}/lib/psych %{buildroot}%{ruby_vendorlibdir}/psych
ln -s %{gem_dir}/gems/psych-%{psych_version}/lib/psych.rb %{buildroot}%{ruby_vendorlibdir}/psych.rb
ln -s %{gem_archdir}/gems/psych-%{psych_version}/psych.so %{buildroot}%{ruby_vendorarchdir}/psych.so

# Note: minitest, power_assert, and other new bundled gems are different in Ruby 2.2+
# and are built in gem_dir, so they don't need to move like the ones above.
# Same with old default gems that changed to bundled gems, like rake.

# net-telnet was made a bundled gem, but is unmaintained.
rm -rf %{buildroot}%{gem_dir}/gems/net-telnet-*
rm -f %{buildroot}%{gem_dir}/specifications/net-telnet-*.gemspec

# Don't ship built .gem files
rm -rf %{buildroot}%{gem_dir}/cache/*

# Adjust the gemspec files so that the gems will load properly
sed -i '/^end$/ i\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/rake-%{rake_version}.gemspec

sed -i '/^end$/ i\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec

sed -i '/^end$/ i\
  s.require_paths = ["lib"]\
  s.extensions = ["bigdecimal.so"]' %{buildroot}%{gem_dir}/specifications/bigdecimal-%{bigdecimal_version}.gemspec

sed -i '/^end$/ i\
  s.require_paths = ["lib"]\
  s.extensions = ["io/console.so"]' %{buildroot}%{gem_dir}/specifications/io-console-%{io_console_version}.gemspec

sed -i '/^end$/ i\
  s.require_paths = ["lib"]\
  s.extensions = ["json/ext/parser.so", "json/ext/generator.so"]' %{buildroot}%{gem_dir}/specifications/json-%{json_version}.gemspec

%if %{with minitest_package}
sed -i '/^end$/ i\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/minitest-%{minitest_version}.gemspec
%endif

# Move man pages into proper location
mv %{buildroot}%{gem_dir}/gems/rake-%{rake_version}/doc/rake.1 %{buildroot}%{_mandir}/man1/rake%{major_minor_version}.1

# Install a tapset and fix up the path to the library.
mkdir -p %{buildroot}%{tapset_dir}
sed -e "s|@LIBRARY_PATH@|%{tapset_libdir}/libruby.so.%{ruby_version}|" \
  %{SOURCE2} > %{buildroot}%{tapset_dir}/libruby.so.%{ruby_version}.stp
# Escape '*/' in comment.
sed -i -r "s|( \*.*\*)\/(.*)|\1\\\/\2|" %{buildroot}%{tapset_dir}/libruby.so.%{ruby_version}.stp

# Managed by alternatives
rm %{buildroot}%{_libdir}/libruby.so

# Create a symbolic link from the versioned library to a generically named library in this version's directory
# for unversioned libraries
ln -s ../../libruby.so.%{ruby_version} %{buildroot}%{ruby_libarchdir}/libruby.so
# Add Ruby's default search path to the linker search path when building binary Ruby modules. This allows linking
# to work when multiple versions of Ruby are installed
# CONFIG["LIBRUBYARG"] = "-L$(archdir) $(LIBRUBYARG_SHARED)"
sed -i -e 's/$(LIBRUBYARG_SHARED)/-L$(archlibdir)\/ruby\/2.5\/ $(LIBRUBYARG_SHARED)/' %{buildroot}%{ruby_libarchdir}/rbconfig.rb
sed -i -e 's/-l$(RUBY_SO_NAME)/-L$(archlibdir)\/ruby\/2.5\/ -l$(RUBY_SO_NAME)/' %{buildroot}%{ruby_libarchdir}/rbconfig.rb

# Create owned local directories or rubygems throws an exception when looking for the gemspec files in /usr/local
mkdir -p %{buildroot}%{_prefix}/local/share/ruby/gems/%{major_minor_version}


find %{buildroot}%{gem_dir} \( -name .gitignore -o -name .travis.yml \) -print0 | xargs -0 rm
rm %{buildroot}%{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/xmlrpc.gemspec


%clean
rm -rf %{buildroot}

%check
# Check RubyGems version correctness.
[ "`make --quiet runruby TESTRUN_SCRIPT='bin/gem -v' | tail -1`" == '%{rubygems_version}' ]
# Check Molinillo version correctness.
[ "`make --quiet runruby TESTRUN_SCRIPT=\"-e \\\"module Gem; module Resolver; end; end; require 'rubygems/resolver/molinillo/lib/molinillo/gem_metadata'; puts Gem::Resolver::Molinillo::VERSION\\\"\" | tail -1`" \
  == '%{molinillo_version}' ]


# Check if systemtap is supported.
make runruby TESTRUN_SCRIPT=%{SOURCE13}

# TestSignal#test_hup_me hangs up the test suite.
# http://bugs.ruby-lang.org/issues/8997
sed -i '/def test_hup_me/,/end if Process.respond_to/ s/^/#/' test/ruby/test_signal.rb

# Segmentation fault.
# https://bugs.ruby-lang.org/issues/9198
sed -i '/^  def test_machine_stackoverflow/,/^  end/ s/^/#/' test/ruby/test_exception.rb

# https://bugs.ruby-lang.org/issues/11480
# Once seen: http://koji.fedoraproject.org/koji/taskinfo?taskID=12556650
rm -v bootstraptest/test_fork.rb

make check TESTS="-v"

%post
%{_sbindir}/update-alternatives \
    --install %{_bindir}/ruby              ruby       %{_bindir}/ruby%{major_minor_version} %{priority} \
    --slave   %{_bindir}/erb               erb        %{_bindir}/erb%{major_minor_version} \
    --slave   %{_bindir}/irb               irb        %{_bindir}/irb%{major_minor_version} \
    --slave   %{_bindir}/gem               gem        %{_bindir}/gem%{major_minor_version} \
    --slave   %{_bindir}/rake      rake       %{_bindir}/rake%{major_minor_version} \
    --slave   %{_bindir}/rdoc      rdoc       %{_bindir}/rdoc%{major_minor_version} \
    --slave   %{_bindir}/ri      ri       %{_bindir}/ri%{major_minor_version} \
    --slave   %{_mandir}/man1/ruby.1.gz    ruby.1     %{_mandir}/man1/ruby%{major_minor_version}.1.gz \
    --slave   %{_mandir}/man1/erb.1.gz     erb.1      %{_mandir}/man1/erb%{major_minor_version}.1.gz \
    --slave   %{_mandir}/man1/irb.1.gz     irb.1      %{_mandir}/man1/irb%{major_minor_version}.1.gz \
    --slave   %{_mandir}/man1/rake.1.gz    rake.1     %{_mandir}/man1/rake%{major_minor_version}.1.gz \
    --slave   %{_mandir}/man1/ri.1.gz    ri.1       %{_mandir}/man1/ri%{major_minor_version}.1.gz \
    --slave   %{_libdir}/pkgconfig/ruby.pc ruby.pc    %{_libdir}/pkgconfig/ruby-%{major_minor_version}.pc

%preun
if [ $1 -eq 0 ]; then
    %{_sbindir}/update-alternatives --remove ruby %{_bindir}/ruby%{major_minor_version}
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%doc BSDL
%doc COPYING
%lang(ja) %doc COPYING.ja
%doc GPL
%doc LEGAL
%ghost %{_bindir}/erb
%{_bindir}/erb%{major_minor_version}
%ghost %{_bindir}/ruby
%{_bindir}/ruby%{major_minor_version}
%ghost %{_mandir}/man1/erb.1.gz
%{_mandir}/man1/erb%{major_minor_version}*
%ghost %{_mandir}/man1/ruby.1.gz
%{_mandir}/man1/ruby%{major_minor_version}*
%if %{without rake_package}
%exclude %{_bindir}/rake%{major_minor_version}
%exclude %{_mandir}/man1/rake%{major_minor_version}*
%exclude %{gem_dir}/gems/rake-%{rake_version}
%exclude %{gem_dir}/specifications/rake-%{rake_version}.gemspec
%endif
%if %{without rdoc_package}
%exclude %{_bindir}/rdoc%{major_minor_version}
%exclude %{_bindir}/ri%{major_minor_version}
%exclude %{_mandir}/man1/ri%{major_minor_version}*
%exclude %{gem_dir}/gems/rdoc-%{rdoc_version}
%exclude %{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec
%endif
%if %{without json_package}
%exclude %{gem_archdir}/gems/json-%{json_version}
%exclude %{gem_dir}/gems/json-%{json_version}
%exclude %{gem_dir}/specifications/json-%{json_version}.gemspec
%endif
%if %{without minitest_package}
%exclude %{gem_dir}/gems/minitest-%{minitest_version}
%exclude %{gem_dir}/specifications/minitest-%{minitest_version}.gemspec
%endif
%if %{without power_assert_package}
%exclude %{gem_dir}/gems/power_assert-%{power_assert_version}
%exclude %{gem_dir}/specifications/power_assert-%{power_assert_version}.gemspec
%endif
%if %{without did_you_mean_package}
%exclude %{gem_dir}/gems/did_you_mean-%{did_you_mean_version}
%exclude %{gem_dir}/specifications/did_you_mean-%{did_you_mean_version}.gemspec
%endif
%if %{without rubygems_package}
%exclude %{_bindir}/gem%{major_minor_version}
%exclude %{ruby_vendorlibdir}/rubygems.rb
%exclude %{ruby_vendorlibdir}/ubygems.rb
%exclude %{ruby_vendorlibdir}/rubygems
%exclude %{ruby_vendorlibdir}/rbconfig/datadir.rb
%exclude %{gem_dir}/cache
# From rubygems-devel
%exclude %{_sysconfdir}/rpm/macros.rubygems%{base_ver}
%endif


%files devel
%doc BSDL
%doc COPYING
%lang(ja) %doc COPYING.ja
%doc GPL
%doc LEGAL
%doc README.EXT
%lang(ja) %doc README.EXT.ja

%{_sysconfdir}/rpm/macros.ruby%{base_ver}

%{_includedir}/ruby/%{major_minor_version}
%{ruby_libarchdir}/libruby.so
%ghost %{_libdir}/pkgconfig/ruby.pc
%{_libdir}/pkgconfig/ruby-%{major_minor_version}.pc

%files libs
%doc COPYING
%lang(ja) %doc COPYING.ja
%doc GPL
%doc LEGAL
%doc README.md
%lang(ja) %doc README.ja.md
%doc NEWS
%doc doc/NEWS-*
%dir %{_prefix}/local/share/ruby
%dir %{ruby_sitelibdir_parent}
%dir %{ruby_sitelibdir}

%dir %{_prefix}/local/%{_lib}/ruby
%dir %{_prefix}/local/%{_lib}/ruby/site_ruby
%dir %{ruby_sitearchdir}

%dir %{ruby_libdir_parent}
%dir %{ruby_vendorlibdir_parent}
%dir %{ruby_vendorlibdir}

%dir %{ruby_libarchdir_parent}
%dir %{_libdir}/ruby/vendor_ruby
%dir %{ruby_vendorarchdir}

# List all these files explicitly to prevent surprises
# Platform independent libraries.
%dir %{ruby_libdir}
%{ruby_libdir}/*.rb
%if %{with X11}
%exclude %{ruby_libdir}/*-tk.rb
%exclude %{ruby_libdir}/tcltk.rb
%exclude %{ruby_libdir}/tk*.rb
%endif
%{ruby_libdir}/cgi
%{ruby_libdir}/digest
%{ruby_libdir}/drb
%{ruby_libdir}/fiddle
%{ruby_libdir}/forwardable
%exclude %{ruby_libdir}/irb
%exclude %{ruby_libdir}/irb.rb
%{ruby_libdir}/matrix
%{ruby_libdir}/net
%{ruby_libdir}/openssl
%{ruby_libdir}/optparse
%{ruby_libdir}/racc
%{ruby_libdir}/rexml
%{ruby_libdir}/rinda
%{ruby_libdir}/ripper
%{ruby_libdir}/rss
%{ruby_libdir}/shell
%{ruby_libdir}/syslog
%if %{with X11}
%exclude %{ruby_libdir}/tk
%exclude %{ruby_libdir}/tkextlib
%endif
%{ruby_libdir}/unicode_normalize
%{ruby_libdir}/uri
%{ruby_libdir}/webrick
%{ruby_libdir}/yaml
%exclude %{ruby_libdir}/bigdecimal
%exclude %{ruby_libarchdir}/bigdecimal.so
%exclude %{ruby_libdir}/io
%exclude %{ruby_libarchdir}/io/console.so
%exclude %{ruby_vendorlibdir}/psych*
%exclude %{ruby_vendorarchdir}/psych.so

# Platform specific libraries.
%{_libdir}/libruby.so.%{major_minor_version}
%{_libdir}/libruby.so.%{ruby_version}
%dir %{ruby_libarchdir}
%dir %{ruby_libarchdir}/cgi
%{ruby_libarchdir}/cgi/escape.so
%{ruby_libarchdir}/continuation.so
%{ruby_libarchdir}/coverage.so
%{ruby_libarchdir}/date_core.so
%{ruby_libarchdir}/dbm.so
%dir %{ruby_libarchdir}/digest
%{ruby_libarchdir}/digest.so
%{ruby_libarchdir}/digest/bubblebabble.so
%{ruby_libarchdir}/digest/md5.so
%{ruby_libarchdir}/digest/rmd160.so
%{ruby_libarchdir}/digest/sha1.so
%{ruby_libarchdir}/digest/sha2.so
%dir %{ruby_libarchdir}/enc
%{ruby_libarchdir}/enc/big5.so
%{ruby_libarchdir}/enc/cp949.so
%{ruby_libarchdir}/enc/emacs_mule.so
%{ruby_libarchdir}/enc/encdb.so
%{ruby_libarchdir}/enc/euc_jp.so
%{ruby_libarchdir}/enc/euc_kr.so
%{ruby_libarchdir}/enc/euc_tw.so
%{ruby_libarchdir}/enc/gb18030.so
%{ruby_libarchdir}/enc/gb2312.so
%{ruby_libarchdir}/enc/gbk.so
%{ruby_libarchdir}/enc/iso_8859_1.so
%{ruby_libarchdir}/enc/iso_8859_10.so
%{ruby_libarchdir}/enc/iso_8859_11.so
%{ruby_libarchdir}/enc/iso_8859_13.so
%{ruby_libarchdir}/enc/iso_8859_14.so
%{ruby_libarchdir}/enc/iso_8859_15.so
%{ruby_libarchdir}/enc/iso_8859_16.so
%{ruby_libarchdir}/enc/iso_8859_2.so
%{ruby_libarchdir}/enc/iso_8859_3.so
%{ruby_libarchdir}/enc/iso_8859_4.so
%{ruby_libarchdir}/enc/iso_8859_5.so
%{ruby_libarchdir}/enc/iso_8859_6.so
%{ruby_libarchdir}/enc/iso_8859_7.so
%{ruby_libarchdir}/enc/iso_8859_8.so
%{ruby_libarchdir}/enc/iso_8859_9.so
%{ruby_libarchdir}/enc/koi8_r.so
%{ruby_libarchdir}/enc/koi8_u.so
%{ruby_libarchdir}/enc/shift_jis.so
%dir %{ruby_libarchdir}/enc/trans
%{ruby_libarchdir}/enc/trans/big5.so
%{ruby_libarchdir}/enc/trans/chinese.so
%{ruby_libarchdir}/enc/trans/ebcdic.so
%{ruby_libarchdir}/enc/trans/emoji.so
%{ruby_libarchdir}/enc/trans/emoji_iso2022_kddi.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_docomo.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_kddi.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_softbank.so
%{ruby_libarchdir}/enc/trans/escape.so
%{ruby_libarchdir}/enc/trans/gb18030.so
%{ruby_libarchdir}/enc/trans/gbk.so
%{ruby_libarchdir}/enc/trans/iso2022.so
%{ruby_libarchdir}/enc/trans/japanese.so
%{ruby_libarchdir}/enc/trans/japanese_euc.so
%{ruby_libarchdir}/enc/trans/japanese_sjis.so
%{ruby_libarchdir}/enc/trans/korean.so
%{ruby_libarchdir}/enc/trans/single_byte.so
%{ruby_libarchdir}/enc/trans/transdb.so
%{ruby_libarchdir}/enc/trans/utf8_mac.so
%{ruby_libarchdir}/enc/trans/utf_16_32.so
%{ruby_libarchdir}/enc/utf_16be.so
%{ruby_libarchdir}/enc/utf_16le.so
%{ruby_libarchdir}/enc/utf_32be.so
%{ruby_libarchdir}/enc/utf_32le.so
%{ruby_libarchdir}/enc/windows_1250.so
%{ruby_libarchdir}/enc/windows_1251.so
%{ruby_libarchdir}/enc/windows_1252.so
%{ruby_libarchdir}/enc/windows_1253.so
%{ruby_libarchdir}/enc/windows_1254.so
%{ruby_libarchdir}/enc/windows_1257.so
%{ruby_libarchdir}/enc/windows_31j.so
%{ruby_libarchdir}/etc.so
%{ruby_libarchdir}/fcntl.so
%{ruby_libarchdir}/fiber.so
%{ruby_libarchdir}/fiddle.so
%{ruby_libarchdir}/gdbm.so
%dir %{ruby_libarchdir}/io
%{ruby_libarchdir}/io/nonblock.so
%{ruby_libarchdir}/io/wait.so
%{ruby_libarchdir}/nkf.so
%{ruby_libarchdir}/objspace.so
%{ruby_libarchdir}/openssl.so
%{ruby_libarchdir}/pathname.so
%{ruby_libarchdir}/pty.so
%dir %{ruby_libarchdir}/racc
%{ruby_libarchdir}/racc/cparse.so
%dir %{ruby_libarchdir}/rbconfig
%{ruby_libarchdir}/rbconfig.rb
%{ruby_libarchdir}/rbconfig/sizeof.so
%{ruby_libarchdir}/readline.so
%{ruby_libarchdir}/ripper.so
%{ruby_libarchdir}/sdbm.so
%{ruby_libarchdir}/socket.so
%{ruby_libarchdir}/stringio.so
%{ruby_libarchdir}/strscan.so
%{ruby_libarchdir}/syslog.so
%if %{with X11}
%exclude %{ruby_libarchdir}/tcltklib.so
%exclude %{ruby_libarchdir}/tkutil.so
%endif
%{ruby_libarchdir}/zlib.so

%{tapset_dir}/libruby.so.%{ruby_version}.stp

%{gem_dir}/specifications/test-unit-*.gemspec
%{gem_dir}/gems/test-unit-*

%{gem_dir}/specifications/openssl-%{openssl_version}.gemspec

%dir %{_libdir}/ruby/gems
%dir %{gem_archdir}

%if %{with rubygems_package}
%files -n rubygems%{base_ver}
%{_bindir}/gem%{major_minor_version}
%ghost %{_bindir}/gem
%dir %{ruby_vendorlibdir}/rubygems
%dir %{_datadir}/ruby/gems
%dir %{gem_dir}
%dir %{gem_dir}/build_info
%dir %{gem_dir}/cache
%dir %{gem_dir}/doc
%dir %{gem_dir}/extensions
%dir %{gem_dir}/gems
%dir %{gem_dir}/specifications
%dir %{gem_dir}/specifications/default
%dir %{_prefix}/local/share/ruby/gems/%{major_minor_version}
%{ruby_vendorlibdir}/rubygems.rb
%{ruby_vendorlibdir}/rubygems/*

%{gem_dir}/specifications/default/cmath-1.0.0.gemspec
%{gem_dir}/specifications/default/csv-1.0.0.gemspec
%{gem_dir}/specifications/default/date-1.0.0.gemspec
%{gem_dir}/specifications/default/dbm-1.0.0.gemspec
%{gem_dir}/specifications/default/etc-1.0.0.gemspec
%{gem_dir}/specifications/default/fcntl-1.0.0.gemspec
%{gem_dir}/specifications/default/fiddle-1.0.0.gemspec
%{gem_dir}/specifications/default/fileutils-1.0.2.gemspec
%{gem_dir}/specifications/default/gdbm-2.0.0.gemspec
%{gem_dir}/specifications/default/ipaddr-1.2.0.gemspec
%{gem_dir}/specifications/default/scanf-1.0.0.gemspec
%{gem_dir}/specifications/default/sdbm-1.0.0.gemspec
%{gem_dir}/specifications/default/stringio-0.0.1.gemspec
%{gem_dir}/specifications/default/strscan-1.0.0.gemspec
%{gem_dir}/specifications/default/webrick-1.4.2.1.gemspec
%{gem_dir}/specifications/default/zlib-1.0.0.gemspec

%files -n rubygems%{base_ver}-devel
%{_sysconfdir}/rpm/macros.rubygems%{base_ver}
%endif

%if %{with rake_package}
%files -n rubygem%{base_ver}-rake
%{_bindir}/rake%{major_minor_version}
%ghost %{_bindir}/rake
%{gem_dir}/gems/rake-%{rake_version}
%{gem_dir}/specifications/rake-%{rake_version}.gemspec
%ghost %{_mandir}/man1/rake.1.gz
%{_mandir}/man1/rake%{major_minor_version}.1*
%endif

%files irb
%ghost %{_bindir}/irb
%{_bindir}/irb%{major_minor_version}
%{ruby_libdir}/irb.rb
%{ruby_libdir}/irb
%ghost %{_mandir}/man1/irb.1.gz
%{_mandir}/man1/irb%{major_minor_version}.1*

%if %{with rdoc_package}
%files -n rubygem%{base_ver}-rdoc
%ghost %{_bindir}/rdoc
%{_bindir}/rdoc%{major_minor_version}
%ghost %{_bindir}/ri
%{_bindir}/ri%{major_minor_version}
%{gem_dir}/gems/rdoc-%{rdoc_version}
%{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec
%ghost %{_mandir}/man1/ri.1.gz
%{_mandir}/man1/ri%{major_minor_version}.1*
%endif

%files doc
%doc README.md
%lang(ja) %doc README.ja.md
%doc ChangeLog
%doc doc/ChangeLog-*
%doc ruby-exercise.stp
%{_datadir}/ri/%{major_minor_version}
%if %{with doc_capi}
%{_docdir}/ruby/capi
%endif

%files -n rubygem%{base_ver}-bigdecimal
%{ruby_libdir}/bigdecimal
%{ruby_libarchdir}/bigdecimal.so
%{gem_archdir}/gems/bigdecimal-%{bigdecimal_version}
%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}
%{gem_dir}/specifications/bigdecimal-%{bigdecimal_version}.gemspec

%if %{with did_you_mean_package}
%files -n rubygem%{base_ver}-did_you_mean
%{gem_dir}/gems/did_you_mean-%{did_you_mean_version}
%exclude %{gem_dir}/gems/did_you_mean-%{did_you_mean_version}/.*
%{gem_dir}/specifications/did_you_mean-%{did_you_mean_version}.gemspec
%endif

%files -n rubygem%{base_ver}-io-console
%{ruby_libdir}/io
%{ruby_libarchdir}/io/console.so
%{gem_archdir}/gems/io-console-%{io_console_version}
%{gem_dir}/gems/io-console-%{io_console_version}
%{gem_dir}/specifications/io-console-%{io_console_version}.gemspec

%if %{with json_package}
%files -n rubygem%{base_ver}-json
%{gem_archdir}/gems/json-%{json_version}
%{gem_dir}/gems/json-%{json_version}
%{gem_dir}/specifications/json-%{json_version}.gemspec
%endif

%if %{with minitest_package}
%files -n rubygem%{base_ver}-minitest5
%{gem_dir}/gems/minitest-%{minitest_version}
%exclude %{gem_dir}/gems/minitest-%{minitest_version}/.*
%{gem_dir}/specifications/minitest-%{minitest_version}.gemspec
%endif

%if %{with power_assert_package}
%files -n rubygem%{base_ver}-power_assert
%{gem_dir}/gems/power_assert-%{power_assert_version}
%exclude %{gem_dir}/gems/power_assert-%{power_assert_version}/.*
%{gem_dir}/specifications/power_assert-%{power_assert_version}.gemspec
%endif

%files -n rubygem%{base_ver}-psych
%{ruby_vendorlibdir}/psych
%{ruby_vendorlibdir}/psych.rb
%{ruby_vendorarchdir}/psych.so
%{gem_archdir}/gems/psych-%{psych_version}
%{gem_dir}/gems/psych-%{psych_version}
%{gem_dir}/specifications/psych-%{psych_version}.gemspec

%files -n rubygem%{base_ver}-xmlrpc
%license %{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/LICENSE.txt
%dir %{gem_dir}/gems/xmlrpc-%{xmlrpc_version}
%{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/Gemfile
%{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/Rakefile
%doc %{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/README.md
%{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/bin
%{gem_dir}/gems/xmlrpc-%{xmlrpc_version}/lib
%{gem_dir}/specifications/xmlrpc-%{xmlrpc_version}.gemspec



%if %{with X11}
%files tcltk
%{ruby_libdir}/*-tk.rb
%{ruby_libdir}/tcltk.rb
%{ruby_libdir}/tk*.rb
%{ruby_libarchdir}/tcltklib.so
%{ruby_libarchdir}/tkutil.so
%{ruby_libdir}/tk
%{ruby_libdir}/tkextlib
%endif

%changelog
* Fri Jul 19 2019 Trinity Quirk <tquirk@amazon.com>
- Add patch for failing Asia/Tokyo tests

* Thu Jul 18 2019 Trinity Quirk <tquirk@amazon.com>
- Skip a failing rubygems assertion which seems incorrect
- Add patch to repair expired SSL test certs

* Mon Jul 1 2019 Trinity Quirk <tquirk@amazon.com>
- Add patches for CVE-2019-8320 - CVE-2019-8325

* Mon Dec 3 2018 Matt Dees <mattdees@amazon.com>
- Update to 2.4.5

* Mon Apr 2 2018 Matt Dees <mattdees@amazon.com>
- Upload to 2.4.4

* Tue Mar 13 2018 Matt Dees <mattdees@amazon.com>
- Update to 2.4.3

* Mon Sep 25 2017 Matt Dees <mattdees@amazon.com>
- Update to 2.4.2

* Thu Sep 7 2017 Matt Dees <mattdees@amazon.com>
- Remove commented out patch completely

* Fri Aug 18 2017 Matt Dees <mattdees@amazon.com>
- Update ruby to 2.4.x

* Mon Aug 14 2017 Matt Dees <mattdees@amazon.com>
- Update ruby to 2.4.x

* Wed Aug 9 2017 Matt Dees <mattdees@amazon.com>
- import source package GOBI/ruby-2.4.1-79.fc26

* Wed Oct 29 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.4-23
- Update to Ruby 2.1.4.
- Include only vendor directories, not their content (rhbz#1114071).
- Fix "invalid regex" warning for non-rubygem packages (rhbz#1154067).
- Use load macro introduced in RPM 4.12.

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 24 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.1.2-23
- Fix FTBFS 
- Specify tcl/tk 8.6
- Add upstream patch to build with libffi 3.1

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Jaroslav Škarvada <jskarvad@redhat.com>
- Rebuilt for https://fedoraproject.org/wiki/Changes/f21tcl86

* Tue May 20 2014 Josef Stribny <jstribny@redhat.com> - 2.1.2-21
- Update to Ruby 2.1.2

* Tue May 06 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.1-20
- Remove useless exclude (rhbz#1065897).
- Extract load macro into external file and include it.
- Kill bundled certificates.

* Wed Apr 23 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.1-19
- Correctly expand $(prefix) in some Makefiles, e.g. eruby.

* Tue Apr 08 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.1-18
- Update to Ruby 2.1.1.
- Revert regression of Hash#reject.

* Mon Mar 03 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.0-19
- Add RPM dependency generators for RubyGems.

* Mon Feb 10 2014 Josef Stribny <jstribny@redhat.com> - 2.1.0-19
- Don't link cert.pem explicitely

* Wed Jan 15 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.0-18
- Don't generate documentation on unexpected places.
- Detect if rubygems are running under rpmbuild and install gem binary
  extensions into appropriate place.
- Add support for ppc64le arch (rhbz#1053263).
- Re-enable some test cases, which are passing now with Kernel 3.12.8+.
- Backport fix for floating point issues on i686.

* Thu Jan 02 2014 Vít Ondruch <vondruch@redhat.com> - 2.1.0-17
- Upgrade to Ruby 2.1.0.
- Move RPM macros into /usr/lib/rpm/macros.d directory.
- Allow MD5 in OpenSSL for tests.

* Tue Jul 30 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-15
- Move Psych symlinks to vendor dir, to prevent F18 -> F19 upgrade issues
  (rhbz#988490).

* Mon Jul 15 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-14
- Add forgotten psych.rb link into rubygem-psych to fix "private method `load'
  called for Psych:Moduler" error (rhbz#979133).

* Thu Jul 11 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-13
- Fixes multilib conlicts of .gemspec files.
- Make symlinks for psych gem to ruby stdlib dirs (rhbz#979133).
- Use system-wide cert.pem.

* Thu Jul 04 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-12
- Fix RubyGems search paths when building gems with native extension
  (rhbz#979133).

* Tue Jul 02 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-11
- Fix RubyGems version.

* Tue Jul 02 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-10
- Better support for build without configuration (rhbz#977941).

* Mon Jul 01 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.247-9
- Update to Ruby 2.0.0-p247 (rhbz#979605).
- Fix CVE-2013-4073.
- Fix for wrong makefiles created by mkmf (rhbz#921650).
- Add support for ABRT autoloading.

* Fri May 17 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.195-8
- Update to Ruby 2.0.0-p195 (rhbz#917374).
- Fix object taint bypassing in DL and Fiddle (CVE-2013-2065).
- Fix build against OpenSSL with enabled ECC curves.
- Add aarch64 support (rhbz#926463).

* Fri Apr 19 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-7
- Macro definition moved into macros.ruby and macros.rubygems files.
- Added filtering macros.
- Filter automatically generated provides of private libraries (rhbz#947408).

* Fri Mar 22 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-6
- Fix RbConfig::CONFIG['exec_prefix'] returns empty string (rhbz#924851).

* Thu Mar 21 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-5
- Make Ruby buildable without rubypick.
- Prevent random test failures.

* Fri Mar 08 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.0.0.0-4
- Don't mark rpm config file as %%config (fpc#259)

* Tue Mar 05 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-3
- Avoid "method redefined;" warnings due to modified operating_system.rb.
- Fix strange paths created during build of binary gems.

* Mon Feb 25 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-2
- Prevent squash of %%gem_install with following line.

* Mon Feb 25 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-1
- Update to Ruby 2.0.0-p0.
- Change %%{ruby_extdir} to %%{ruby_extdir_mri} in preparation for better
  JRuby support.

* Mon Feb 25 2013 Mamoru TASAKA <mtasaka@fedoraprojec.org> - 2.0.0.0-0.3.r39387
- Move test-unit.gemspec to -libs subpackage for now because rubygems
  2.0.0 does not create this

* Fri Feb 22 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-0.2.r39387
- Fix issues with wrong value of Rubygem's shebang introduced in r39267.

* Fri Feb 22 2013 Vít Ondruch <vondruch@redhat.com> - 2.0.0.0-0.1.r39387
- Upgrade to Ruby 2.0.0 (r39387).
- Introduce %%gem_install macro.
- Build against libdb instead of libdb4 (rhbz#894022).
- Move native extensions from exts to ruby directory.
- Enable most of the PPC test suite.
- Change ruby(abi) -> ruby(release).
- Rename ruby executable to ruby-mri, to be prepared for RubyPick.
- Add ruby(runtime_executable) virtual provide, which is later used
  by RubyPick.
- RDoc now depends on JSON.
- Try to make -doc subpackage noarch again, since the new RDoc should resolve
  the arch dependent issues (https://github.com/rdoc/rdoc/issues/71).
- Enable SystemTap support.
- Add TapSet for Ruby.
- Split Psych into rubygem-psych subpackage.

* Mon Feb 11 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.385-28
- Update to 1.9.3 p385

* Sat Jan 19 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.374-27
- Update to 1.9.3 p374
- Fix provided variables in pkgconfig (bug 789532:
  Vít Ondruch <vondruch@redhat.com>)

* Fri Jan 18 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-26
- Provide non-versioned pkgconfig file (bug 789532)
- Use db5 on F-19 (bug 894022)

* Wed Jan 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-25
- Backport fix for the upstream PR7629, save the proc made from the given block
  (bug 895173)

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-24
- Update to 1.9.3.362

* Mon Dec 03 2012 Jaromir Capik <jcapik@redhat.com> - 1.9.3.327-23
- Skipping test_parse.rb (fails on ARM at line 787)
- http://bugs.ruby-lang.org/issues/6899

* Sun Nov 11 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-23
- Skip test_str_crypt (on rawhide) for now (upstream bug 7312)

* Sat Nov 10 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-22
- Ignore some network related tests

* Sat Nov 10 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-21
- Update to 1.9.3.327
- Fix Hash-flooding DoS vulnerability on MurmurHash function
  (CVE-2012-5371)

* Sat Oct 13 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.286-19
- Update to 1.9.3 p286
- Don't create files when NUL-containing path name is passed
  (bug 865940, CVE-2012-4522)

* Thu Oct 04 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.9.3.194-18
- Patch from trunk for CVE-2012-4464, CVE-2012-4466

* Thu Sep 06 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-17
- Split documentation into -doc subpackage (rhbz#854418).

* Tue Aug 14 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-16
- Revert the dependency of ruby-libs on rubygems (rhbz#845011, rhbz#847482).

* Wed Aug 01 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-15
- ruby-libs must require rubygems (rhbz#845011).

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.3.194-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-13
- Make the bigdecimal gem a runtime dependency of Ruby.

* Mon Jun 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-12
- Make symlinks for bigdecimal and io-console gems to ruby stdlib dirs (RHBZ 829209).

* Tue May 29 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-11
- Fix license to contain Public Domain.
- macros.ruby now contains unexpanded macros.

* Sun Apr 22 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.9.3.194-10.1
- Bump release

* Fri Apr 20 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-1
- Update to Ruby 1.9.3-p194.

* Mon Apr 09 2012 Karsten Hopp <karsten@redhat.com> 1.9.3.125-3
- disable check on ppc(64), RH bugzilla 803698

* Wed Feb 29 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.9.3.125-2
- Temporarily disable make check on ARM until it's fixed upstream. Tracked in RHBZ 789410

* Mon Feb 20 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.125-1
- Upgrade to Ruby 1.9.3-p125.

* Sun Jan 29 2012 Mamoru Tasaka <mtasaka@fedoraprpject.org> - 1.9.3.0-7
- Make mkmf.rb verbose by default

* Thu Jan 26 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-6
- Relax dependencies to allow external updates of bundled gems.

* Wed Jan 18 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-5
- Initial release of Ruby 1.9.3.
- Add rubygems dependency on io-console for user interactions.
- Gems license clarification.

* Tue Jan 17 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-4
- Bundled gems moved into dedicated directories and subpackages.
- Create and own RubyGems directories for binary extensions.
- Fix build with GCC 4.7.

* Mon Jan 16 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-3
- Fix RHEL build.
- Fixed directory ownership.
- Verose build output.

* Sun Jan 15 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-2
- Install RubyGems outside of Ruby directory structure.
- RubyGems has not its own -devel subpackage.
- Enhanced macros.ruby and macros.rubygems.
- All tests are green now (bkabrda).

* Sat Jan 14 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-1
- Initial package

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.7.357-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 29 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.357-1
- Update to 1.8.7p357
- Randomize hash on process startup (CVE-2011-4815, bug 750564)

* Fri Dec 23 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.352-2
- dont normalise arm cpus to arm
- there is something weird about how ruby choses where to put bits

* Thu Nov 17 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-3
- F-17: kill gdbm support for now due to licensing compatibility issue

* Sat Oct  1 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-2
- F-17: rebuild against new gdbm

* Sat Jul 16 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-1
- Update to 1.8.7 p352
- CVE-2011-2686 is fixed in this version (bug 722415)
- Update ext/tk to the latest git
- Remove duplicate path entry (bug 718695)

* Thu Jul 14 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.334-4
- Once fix FTBFS (bug 716021)

* Mon Jul 11 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.334-3
- normalise arm cpus to arm

* Mon May 30 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.334-2
- Own %%{_normalized_cpu}-%%{_target_os} directory (bug 708816)

* Sat Feb 19 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.334-1
- Update to 1.8.7 p334

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.7.330-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jan 02 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.330-2
- nomalise the 32 bit sparc archs to sparc

* Sun Dec 26 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.330-1
- Update to 1.8.7 p330
- ext/tk updated to the newest header

* Thu Nov  4 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.302-2
- Avoid multilib conflict on -libs subpackage (bug 649174)

* Mon Aug 23 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.302-1
- Update to 1.8.7.302
- CVE-2010-0541 (bug 587731) is fixed in this version
- Update ext/tk to the latest head

* Mon Aug  2 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.299-5
- More cleanup of spec file, expecially for rpmlint issue
- build ri files in %%build

* Mon Jul 26 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.299-4
- Cleanup spec file
- Make -irb, -rdoc subpackage noarch
- Make dependencies between arch-dependent subpackages isa specific
- Improve sample documentation gathering

* Mon Jul 12 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-3
- updated packaged based on feedback (from mtasaka)
- added comments to all patches / sources
- obsoleted ruby-mode, as it's now provided by the emacs package itself
- readded missing documentation
- various small compatability/regression fixes

* Tue Jul 06 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-2
- readded bits to pull tk package from upstream source branch
- removed unecessary .tk.old dir
- renamed macros which may cause confusion, removed unused ones

* Thu Jun 24 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-1
- integrate more of jmeyering's and mtaska's feedback
- removed emacs bits that are now shipped with the emacs package
- various patch and spec cleanup
- rebased to ruby 1.8.7 patch 299, removed patches no longer needed:
   ruby-1.8.7-openssl-1.0.patch, ruby-1.8.7-rb_gc_guard_ptr-optimization.patch

* Wed Jun 23 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-5
- Various fixes

* Wed Jun 23 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-4
- Fixed incorrect paths in 1.8.7 rpm

* Tue Jun 22 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-3
- Integrated Jim Meyering's feedback and changes in to:
- remove trailing blanks
- placate rpmlint
- ruby_* definitions: do not use trailing slashes in directory names
- _normalized_cpu: simplify definition

* Mon Jun 21 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-2
- Integrate mtasaka's feedback and changes
- patch101 ruby_1_8_7-rb_gc_guard_ptr-optimization.patch

* Tue Jun 15 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-1
- Initial Ruby 1.8.7 specfile

* Wed May 19 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-5
- Retry for bug 559158, Simplify the OpenSSL::Digest class
  pull more change commits from ruby_1_8 branch

* Mon May 17 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-4
- Patch36 (ruby-1.8.x-RHASH_SIZE-rb_hash_lookup-def.patch)
  also backport rb_hash_lookup definition (bug 592936)

* Thu May 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-3
- ruby-1.8.x-null-class-must-be-Qnil.patch (bug 530407)
- Recreate some patches using upstream svn when available, and
  add some comments for patches

* Tue May 11 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-2
- tcltk: Give up using potentially unmaintained ruby_1_8_6 branch
  and instead completely replace with ruby_1_8 branch head
  (at this time, using rev 27738)
  (seems to fix 560053, 590503)
- Fix Japanese encoding strings under ruby-tcltk/ext/tk/sample/

* Tue Apr 27 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-1
- Update to 1.8.6 p 399 (bug 579675)
- Patch to fix gc bug causing open4 crash (bug 580993)

* Fri Mar 12 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.388-9
- F-14: rebuild against new gdbm

* Thu Jan 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- Once revert the previous change (patch34)

* Wed Jan 27 2010 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.388-8
- Backport openssl/digest functions providing digest and hexdigest functions
  directly in OpenSSL::Digest.methods
- Make sure that Red Hat people version their changelog entries
- This is actually release #1, but now needs to be release #7

* Mon Jan 18 2010 Akira TAGOH <tagoh@redhat.com> - 1.8.6.388-1
- Add conditional for RHEL.

* Wed Jan 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-6
- CVE-2009-4492 ruby WEBrick log escape sequence (bug 554485)

* Wed Dec  9 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-5
- Change mkmf.rb to use LIBRUBYARG_SHARED so that have_library() works
  without libruby-static.a (bug 428384)
- And move libruby-static.a to -static subpackage

* Thu Oct 29 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-4
- Use bison to regenerate parse.c to keep the original format of error
  messages (bug 530275 comment 4)

* Sun Oct 25 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-3
- Patch so that irb saves its history (bug 518584, ruby issue 1556)

* Sat Oct 24 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-2
- Update to 1.8.6 patchlevel 383 (bug 520063)

* Wed Oct 14 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-5
- Much better idea for Patch31 provided by Akira TAGOH <tagoh@redhat.com>

* Wed Oct 14 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-4
- Fix the search path of ri command for ri manuals installed with gem
  (bug 528787)

* Wed Aug 26 2009 Tomas Mraz <tmraz@redhat.com> - 1.8.6.369-3
- Rebuild against new openssl

* Thu Jul 23 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-2
- Make sure that readline.so is linked against readline 5 because
  Ruby is under GPLv2

* Sat Jun 20 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.369-1
- New patchlevel fixing CVE-2009-1904
- Fix directory on ARM (#506233, Kedar Sovani)

* Sun May 31 2009 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.368-1
- New upstream release (p368)

* Sat Apr 11 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.287-8
- Merge Review fix (#226381)

* Wed Mar 18 2009 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.287-7
- Fix regression in CVE-2008-3790 (#485383)

* Mon Mar 16 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.287-6
- Again use -O2 optimization level
- i586 should search i386-linux directory (on <= F-11)

* Thu Mar 05 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.287-5
- Rebuild for gcc4.4

* Fri Feb 27 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.287-3
- CVE-2008-5189: CGI header injection.

* Wed Oct  8 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.287-2
- CVE-2008-3790: DoS vulnerability in the REXML module.

* Sat Aug 23 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.287-1
- New upstream release.
- Security fixes.
  - CVE-2008-3655: Ruby does not properly restrict access to critical
                   variables and methods at various safe levels.
  - CVE-2008-3656: DoS vulnerability in WEBrick.
  - CVE-2008-3657: Lack of taintness check in dl.
  - CVE-2008-1447: DNS spoofing vulnerability in resolv.rb.
  - CVE-2008-3443: Memory allocation failure in Ruby regex engine.
- Remove the unnecessary backported patches.

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.8.6.230-5
- rebuild against db4-4.7

* Tue Jul  1 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-4
- Backported from upstream SVN to fix a segfault issue with Array#fill.

* Mon Jun 30 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-3
- Backported from upstream SVN to fix a segfault issue. (#452825)
- Backported from upstream SVN to fix an integer overflow in rb_ary_fill.

* Wed Jun 25 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-2
- Fix a segfault issue. (#452810)

* Tue Jun 24 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-1
- New upstream release.
- Security fixes. (#452295)
  - CVE-2008-1891: WEBrick CGI source disclosure.
  - CVE-2008-2662: Integer overflow in rb_str_buf_append().
  - CVE-2008-2663: Integer overflow in rb_ary_store().
  - CVE-2008-2664: Unsafe use of alloca in rb_str_format().
  - CVE-2008-2725: Integer overflow in rb_ary_splice().
  - CVE-2008-2726: Integer overflow in rb_ary_splice().
- ruby-1.8.6.111-CVE-2007-5162.patch: removed.
- Build ruby-mode package for all archtectures.

* Tue Mar  4 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.114-1
- Security fix for CVE-2008-1145.
- Improve a spec file. (#226381)
  - Correct License tag.
  - Fix a timestamp issue.
  - Own a arch-specific directory.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.8.6.111-9
- Autorebuild for GCC 4.3

* Tue Feb 19 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-8
- Rebuild for gcc-4.3.

* Tue Jan 15 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-7
- Revert the change of libruby-static.a. (#428384)

* Fri Jan 11 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-6
- Fix an unnecessary replacement for shebang. (#426835)

* Fri Jan  4 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-5
- Rebuild.

* Fri Dec 28 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-4
- Clean up again.

* Fri Dec 21 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-3
- Clean up the spec file.
- Remove ruby-man-1.4.6 stuff. this is entirely the out-dated document.
  this could be replaced by ri.
- Disable the static library building.

* Tue Dec 04 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.8.6.111-2
- Rebuild for openssl bump

* Wed Oct 31 2007 Akira TAGOH <tagoh@redhat.com>
- Fix the dead link.

* Mon Oct 29 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-1
- New upstream release.
- ruby-1.8.6.111-CVE-2007-5162.patch: Update a bit with backporting the changes
   at trunk to enable the fix without any modifications on the users' scripts.
   Note that Net::HTTP#enable_post_connection_check isn't available anymore.
   If you want to disable this post-check, you should give OpenSSL::SSL::VERIFY_NONE
   to Net::HTTP#verify_mode= instead of.

* Mon Oct 15 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.110-2
- Enable pthread support for ppc too. (#201452)
- Fix unexpected dependencies appears in ruby-libs. (#253325)

* Wed Oct 10 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.110-1
- New upstream release.
  - ruby-r12567.patch: removed.
- ruby-1.8.6-CVE-2007-5162.patch: security fix for Net::HTTP that is
  insufficient verification of SSL certificate.

* Thu Aug 23 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-4
- Rebuild

* Fri Aug 10 2007 Akira TAGOH <tagoh@redhat.com>
- Update License tag.

* Mon Jun 25 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-3
- ruby-r12567.patch: backport patch from upstream svn to get rid of
  the unnecessary declarations. (#245446)

* Wed Jun 20 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-2
- New upstream release.
  - Fix Etc::getgrgid to get the correct gid as requested. (#236647)

* Wed Mar 28 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6-2
- Fix search path breakage. (#234029)

* Thu Mar 15 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6-1
- New upstream release.
- clean up a spec file.

* Tue Feb 13 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.5.12-2
- Rebuild

* Mon Feb  5 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.5.12-1
- New upstream release.

* Mon Dec 11 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5.2-1
- security fix release.

* Fri Oct 27 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-4
- security fix release.
- ruby-1.8.5-cgi-CVE-2006-5467.patch: fix a CGI multipart parsing bug that
  causes the denial of service. (#212396)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 1.8.5-3
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 26 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-2
- fixed rbconfig.rb to refer to DESTDIR for sitearchdir. (#207311)

* Mon Aug 28 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-1
- New upstream release.
- removed the unnecessary patches:
  - ruby-1.8.4-no-eaccess.patch
  - ruby-1.8.4-64bit-pack.patch
  - ruby-1.8.4-fix-insecure-dir-operation.patch
  - ruby-1.8.4-fix-insecure-regexp-modification.patch
  - ruby-1.8.4-fix-alias-safe-level.patch
- build with --enable-pthread except on ppc.
- ruby-1.8.5-hash-memory-leak.patch: backported from CVS to fix a memory leak
  on Hash. [ruby-talk:211233]

* Mon Aug  7 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-12
- owns sitearchdir. (#201208)

* Thu Jul 20 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-11
- security fixes [CVE-2006-3694]
  - ruby-1.8.4-fix-insecure-dir-operation.patch:
  - ruby-1.8.4-fix-insecure-regexp-modification.patch: fixed the insecure
    operations in the certain safe-level restrictions. (#199538)
  - ruby-1.8.4-fix-alias-safe-level.patch: fixed to not bypass the certain
    safe-level restrictions. (#199543)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-10.fc6.1
- rebuild

* Mon Jun 19 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-10
- fixed the wrong file list again. moved tcltk library into ruby-tcltk.
  (#195872)

* Thu Jun  8 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-8
- ruby-deprecated-sitelib-search-path.patch: correct the order of search path.

* Wed Jun  7 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-7
- exclude ppc64 to make ruby-mode package. right now emacs.ppc64 isn't provided
  and buildsys became much stricter.
- ruby-deprecated-sitelib-search-path.patch: applied to add more search path
  for backward compatiblity.
- added byacc to BuildReq. (#194161)

* Wed May 17 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-6
- ruby-deprecated-search-path.patch: added the deprecated installation paths
  to the search path for the backward compatibility.
- added a Provides: ruby(abi) to ruby-libs.
- ruby-1.8.4-64bit-pack.patch: backport patch from upstream to fix unpack("l")
  not working on 64bit arch and integer overflow on template "w". (#189350)
- updated License tag to be more comfortable, and with a pointer to get more
  details, like Python package does. (#179933)
- clean up.

* Wed Apr 19 2006 Akira TAGOH <tagoh@redhat.com>
- ruby-rubyprefix.patch: moved all arch-independent modules under /usr/lib/ruby
  and keep arch-dependent modules under /usr/lib64/ruby for 64bit archs.
  so 'rubylibdir', 'sitelibdir' and 'sitedir' in Config::CONFIG points to
  the kind of /usr/lib/ruby now. (#184199)

* Mon Apr 17 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-4
- correct sitelibdir. (#184198)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb  6 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-3
- ruby-1.8.4-no-eaccess.patch: backported from ruby CVS to avoid conflict
  between newer glibc. (#179835)

* Wed Jan  4 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-2
- ruby-tcltk-multilib.patch: fixed a typo.

* Tue Dec 27 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-1
- New upstream release.
  - fixed a missing return statement. (#140833)
  - fixed an use of uninitialized variable. (#144890)

* Fri Dec 16 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.4.preview2
- updates to 1.8.4-preview2.
- renamed the packages to ruby-* (#175765)
  - irb  -> ruby-irb
  - rdoc -> ruby-rdoc
  - ri   -> ruby-ri
- added tcl-devel and tk-devel into BuildRequires.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov 10 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.3.preview1
- rebuilt against the latest openssl.

* Tue Nov  1 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.2.preview1
- build-deps libX11-devel instead of xorg-x11-devel.

* Mon Oct 31 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.1.preview1
- New upstream release.
- ruby-1.8.2-strscan-memset.patch: removed because it's no longer needed.

* Tue Oct  4 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-4
- moved the documents from ruby-libs to ruby-docs, which contains the arch
  specific thing and to be multilib support. (#168826)

* Mon Oct  3 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-3
- fixed the wrong file list. the external library for tcl/tk was included
  in ruby-libs unexpectedly.

* Mon Sep 26 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-2
- ruby-multilib.patch: added another chunk for multilib. (#169127)

* Wed Sep 21 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-1
- New upstream release.
- Build-Requires xorg-x11-devel instead of XFree86-devel.
- ruby-multilib.patch: applied for only 64-bit archs.
- ruby-1.8.2-xmlrpc-CAN-2005-1992.patch: removed. it has already been in upstream.

* Tue Jun 21 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-9
- ruby-1.8.2-xmlrpc-CAN-2005-1992.patch: fixed the arbitrary command execution
  on XMLRPC server. (#161096)

* Thu Jun 16 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-8
- ruby-1.8.2-tcltk-multilib.patch: applied to get tcltklib.so built. (#160194)

* Thu Apr  7 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-7
- ruby-1.8.2-deadcode.patch: removed the dead code from the source. (#146108)
- make sure that all documentation files in ruby-docs are the world-
  readable. (#147279)

* Tue Mar 22 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-6
- ruby-1.8.2-strscan-memset.patch: fixed an wrong usage of memset(3).

* Tue Mar 15 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-5
- rebuilt

* Tue Jan 25 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-4
- fixed the wrong generation of file manifest. (#146055)
- spec file clean up.

* Mon Jan 24 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-3
- separated out to rdoc package.
- make the dependency of irb for rdoc. (#144708)

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> - 1.8.2-2
- Rebuilt for new readline.

* Wed Jan  5 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-1
- New upstream release.
- ruby-1.8.1-ia64-stack-limit.patch: removed - it's no longer needed.
- ruby-1.8.1-cgi_session_perms.patch: likewise.
- ruby-1.8.1-cgi-dos.patch: likewise.
- generated Ruby interactive documentation - senarated package.
  it's now provided as ri package. (#141806)

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 1.8.1-10
- rebuild against db-4.3.21.

* Wed Nov 10 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-9
- ruby-1.8.1-cgi-dos.patch: security fix [CAN-2004-0983]
- ruby-1.8.1-cgi_session_perms.patch: security fix [CAN-2004-0755]

* Fri Oct 29 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-8
- added openssl-devel and db4-devel into BuildRequires (#137479)

* Wed Oct  6 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-7
- require emacs-common instead of emacs.

* Wed Jun 23 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-4
- updated the documentation.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 04 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-1
- New upstream release.
- don't use any optimization for ia64 to avoid the build failure.
- ruby-1.8.1-ia64-stack-limit.patch: applied to fix SystemStackError when the optimization is disabled.

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-3
- rebuild against db-4.2.52.

* Thu Sep 25 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-2
- rebuild against db-4.2.42.

* Tue Aug  5 2003 Akira TAGOH <tagoh@redhat.com> 1.8.0-1
- New upstream release.

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9.1
- rebuilt

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9
- ruby-1.6.8-castnode.patch: handling the nodes with correct cast.
  use this patch now instead of ruby-1.6.8-fix-x86_64.patch.

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-8
- rebuilt

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-7
- fix the gcc warnings. (#82192)
- ruby-1.6.8-fix-x86_64.patch: correct a patch.
  NOTE: DON'T USE THIS PATCH FOR BIG ENDIAN ARCHITECTURE.
- ruby-1.6.7-long2int.patch: removed.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb  7 2003 Jens Petersen <petersen@redhat.com> - 1.6.8-5
- rebuild against ucs4 tcltk

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 22 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-3
- ruby-1.6.8-multilib.patch: applied to fix the search path issue on x86_64

* Tue Jan 21 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-2
- ruby-1.6.8-require.patch: applied to fix the search bug in require.
- don't apply long2int patch to s390 and s390x. it doesn't work.

* Wed Jan 15 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-1
- New upstream release.
- removed some patches. it's no longer needed.
  - ruby-1.6.7-100.patch
  - ruby-1.6.7-101.patch
  - ruby-1.6.7-102.patch
  - ruby-1.6.7-103.patch
  - 801_extmk.rb-shellwords.patch
  - 801_mkmf.rb-shellwords.patch
  - 804_parse.y-new-bison.patch
  - 805_uri-bugfix.patch
  - ruby-1.6.6-900_XXX_strtod.patch
  - ruby-1.6.7-sux0rs.patch
  - ruby-1.6.7-libobj.patch

* Wed Jan 15 2003 Jens Petersen <petersen@redhat.com> 1.6.7-14
- rebuild to update tcltk deps

* Mon Dec 16 2002 Elliot Lee <sopwith@redhat.com> 1.6.7-13
- Remove ExcludeArch: x86_64
- Fix x86_64 ruby with long2int.patch (ruby was assuming that sizeof(long)
  == sizeof(int). The patch does not fix the source of the problem, just
  makes it a non-issue.)
- _smp_mflags

* Tue Dec 10 2002 Tim Powers <timp@redhat.com> 1.6.7-12
- rebuild to fix broken tcltk deps

* Tue Oct 22 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-11
- use %%configure macro instead of configure script.
- use the latest config.{sub,guess}.
- get archname from rbconfig.rb for %%dir
- applied some patches from Debian:
  - 801_extmk.rb-shellwords.patch: use Shellwords
  - 801_mkmf.rb-shellwords.patch: mkmf.rb creates bad Makefile. the Makefile
    links libruby.a to the target.
  - 803_sample-fix-shbang.patch: all sample codes should be
    s|/usr/local/bin|/usr/bin|g
  - 804_parse.y-new-bison.patch: fix syntax warning.
  - 805_uri-bugfix.patch: uri.rb could not handle correctly broken mailto-uri.
- add ExcludeArch x86_64 temporarily to fix Bug#74581. Right now ruby can't be
  built on x86_64.

* Tue Aug 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-10
- moved sitedir to /usr/lib/ruby/site_ruby again according as our perl and
  python.
- ruby-1.6.7-resolv1.patch, ruby-1.6.7-resolv2.patch: applied to fix 'Too many
  open files - "/etc/resolv.conf"' issue. (Bug#64830)

* Thu Jul 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-9
- add the owned directory.

* Fri Jul 12 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-8
- fix typo.

* Thu Jul 04 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-7
- removed the ruby-mode-xemacs because it's merged to the xemacs sumo.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jun 19 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-5
- fix the stripped binary.
- use the appropriate macros.

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-3
- ruby-1.6.7-libobj.patch: applied to fix autoconf2.53 error.

* Mon Mar 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-2
- ruby-man-1.4.6-jp.tar.bz2: removed.
- ruby-refm-rdp-1.4.7-ja-html.tar.bz2: uses it instead of.
- ruby-1.6.7-500-marshal-proc.patch, ruby-1.6.7-501-class-var.patch:
  removed.
- ruby-1.6.7-100.patch: applied a bug fix patch.
  (ruby-dev#16274: patch for 'wm state')
  (PR#206ja: SEGV handle EXIT)
- ruby-1.6.7-101.patch: applied a bug fix patch.
  (ruby-list#34313: singleton should not be Marshal.dump'ed)
  (ruby-dev#16411: block local var)
- ruby-1.6.7-102.patch: applied a bug fix patch.
  (handling multibyte chars is partially broken)
- ruby-1.6.7-103.patch: applied a bug fix patch.
  (ruby-dev#16462: preserve reference for GC, but link should be cut)

* Fri Mar  8 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-1
- New upstream release.
- ruby-1.6.6-100.patch, ruby-1.6.6-501-ruby-mode.patch:
  removed. these patches no longer should be needed.
- ruby-1.6.7-500-marshal-proc.patch: applied a fix patch.
  (ruby-dev#16178: Marshal::dump should call Proc#call.)
- ruby-1.6.7-501-class-var.patch: applied a fix patch.
  (ruby-talk#35157: class vars broken in 1.6.7)

* Wed Feb 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-5
- Disable alpha because nothing is xemacs for alpha now.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-3
- Fixed the duplicate files.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-2
- Fixed the missing %%defattr

* Fri Feb  1 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-1
- New upstream release.
- Applied bug fix patches:
  - ruby-1.6.6-501-ruby-mode.patch: ruby-talk#30479: disables font-lock
    coloring.
  - ruby-1.6.6-100.patch: ruby-talk#30203: Ruby 1.6.6 bug and fix
                          ruby-list#33047: regex bug
                          PR#230: problem with -d in 1.6.6
- Added ruby-mode and ruby-mode-xemacs packages.
- Ruby works fine for ia64. so re-enable to build with ia64.
  (probably it should be worked for alpha)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jul 19 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.4-2
- Remove Japanese description and summaries; they belong in specspo and
  break rpm
- Clean up specfile
- Mark language specific files (README.jp) as such
- bzip2 sources
- rename the libruby package to ruby-libs for consistency
- Exclude ia64 (doesn't build - the code doesn't seem to be 64-bit clean
  [has been excluded on alpha forever])

* Tue Jul 17 2001 Akira TAGOH <tagoh@redhat.com> 1.6.4-1
- rebuild for Red Hat 7.2

* Mon Jun 04 2001 akira yamada <akira@vinelinux.org>
- upgrade to nwe upstream version 1.6.4.

* Mon Apr 02 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed method cache bug. etc. (Patch103, Patch104)

* Tue Mar 27 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed marshal for bignum bug.
  - fixed scope of constant variables bug.

* Tue Mar 20 2001 akira yamada <akira@vinelinux.org>
- upgraded to new upstream version 1.6.3.

* Fri Feb 09 2001 akira yamada <akira@vinelinux.org>
- fixed bad group for libruby.
- Applied patch: upgraded to cvs version (2001-02-08):
  fixed minor bugs.

* Thu Jan 18 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-15):
  fixed minor bugs(e.g. ruby makes extention librares too large...).

* Wed Jan 10 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-09):
  fixed minor bugs.

* Sat Dec 30 2000 akira yamada <akira@vinelinux.org>
- Applied bug fix patch.

* Mon Dec 25 2000 akira yamada <akira@vinelinux.org>
- Updated to new upstream version 1.6.2.

* Fri Dec 22 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000122019.patch, added ruby_cvs.2000122215.patch
  (upgraded ruby to latest cvs version, 1.6.2-preview4).

* Wed Dec 20 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000121413.patch, added ruby_cvs.2000122019.patch
  (upgraded ruby to latest cvs version).
- new package: libruby

* Thu Dec 14 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000101901.patch, added ruby_cvs.2000121413.patch
  (upgraded ruby to latest cvs version).
- Removed ruby-dev.11262.patch, ruby-dev.11265.patch,
  and ruby-dev.11268.patch (included into above patch).

* Sun Nov 12 2000 MACHINO, Satoshi <machino@vinelinux.org> 1.6.1-0vl9
- build on gcc-2.95.3

* Thu Oct 19 2000 akira yamada <akira@vinelinux.org>
- Added ruby-dev.11268.patch.
- Removed ruby_cvs.2000101117.patch and added ruby_cvs.2000101901.patch
  (upgraded ruby to latest cvs version).
- Added ruby-dev.11262.patch.
- Added ruby-dev.11265.patch.

* Wed Oct 11 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000101117.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 09 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Tue Oct 03 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100218.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 02 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000092718.patch and added ruby_cvs.2000100218.patch
  (upgraded ruby to latest cvs version).

* Wed Sep 27 2000 akira yamada <akira@vinelinux.org>
- Updated to upstream version 1.6.1.
- Removed ruby_cvs.2000082901.patch and added ruby_cvs.2000092718.patch
  (upgraded ruby to latest cvs version).

* Tue Aug 29 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.6.
- removed ruby-dev.10123.patch(included into ruby-1.4.6).
- Added ruby_cvs.2000082901.patch(upgraded ruby to latest cvs version).

* Tue Jun 27 2000 akira yamada <akira@redhat.com>
- Updated manuals to version 1.4.5.

* Sun Jun 25 2000 akira yamada <akira@redhat.com>
- Added ruby-dev.10123.patch.

* Sat Jun 24 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.5.
- Removed ruby_cvs.2000062401.patch(included into ruby-1.4.5).

* Thu Jun 22 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/22/2000 CVS).
- Removed ruby-dev.10054.patch(included into ruby_cvs.patch).
- Renamed to ruby_cvs20000620.patch from ruby_cvs.patch.

* Tue Jun 20 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/20/2000 CVS).
- Removed ruby-list.23190.patch(included into ruby_cvs.patch).
- Added ruby-dev.10054.patch.

* Thu Jun 15 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/12/2000 CVS).
- Added manuals and FAQs.
- Split into ruby, ruby-devel, ruby-tcltk, ruby-docs, irb.

* Tue Jun 13 2000 Mitsuo Hamada <mhamada@redhat.com>
- Updated to version 1.4.4

* Wed Dec 08 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.3

* Mon Sep 20 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2 (Sep 18)

* Fri Sep 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2

* Tue Aug 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.0

* Fri Jul 23 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- 2nd release
- Updated to version 1.2.6(15 Jul 1999)
- striped %%{prefix}/bin/ruby

* Mon Jun 28 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.6(21 Jun 1999)

* Wed Apr 14 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.5

* Fri Apr 09 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.4

* Fri Dec 25 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.2 stable.

* Fri Nov 27 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c9.

* Thu Nov 19 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c8, however it appear short life :-P

* Fri Nov 13 1998 Toru Hoshina <hoshina@best.com>
- Version up.

* Tue Sep 22 1998 Toru Hoshina <hoshina@best.com>
- To make a libruby.so.

* Mon Sep 21 1998 Toru Hoshina <hoshina@best.com>
- Modified SPEC in order to install libruby.a so that it should be used by
  another ruby entention.
- 2nd release.

* Mon Mar 9 1998 Shoichi OZAWA <shoch@jsdi.or.jp>
- Added a powerPC arch part. Thanks, MURATA Nobuhiro <nob@makioka.y-min.or.jp>
