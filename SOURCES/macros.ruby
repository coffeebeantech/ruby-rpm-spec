# Base install directories for standard Ruby libraries
%ruby25_libdir_parent       %{_datadir}/ruby
%ruby25_libarchdir_parent   %{_libdir}/ruby
%ruby25_libdir              %{ruby25_libdir_parent}/2.5
%ruby25_libarchdir          %{ruby25_libarchdir_parent}/2.5

%ruby25_hdrdir              %{_includedir}/ruby/2.5

# Local lib/arch for user installed libraries. Nothing should be
# installed here by the vendor
%ruby25_sitelibdir_parent   %{_prefix}/local/share/ruby/site_ruby
%ruby25_sitelibdir          %{ruby25_sitelibdir_parent}/2.5
%ruby25_sitearchdir         %{_prefix}/local/%{_lib}/ruby/site_ruby/2.5
%ruby25_sitehdrdir          %{_prefix}/local/include/ruby/2.5

# Vendor lib/arch for vendor installed libraries. Nothing should be
# installed here by the user
%ruby25_vendorlibdir_parent %{_datadir}/ruby/vendor_ruby
%ruby25_vendorlibdir        %{ruby25_vendorlibdir_parent}/2.5
%ruby25_vendorarchdir       %{_libdir}/ruby/vendor_ruby/2.5
%ruby25_vendorhdrdir        %{ruby25_hdrdir}

# For ruby packages we want to filter out any provides caused by private
# libs in %%{ruby25_vendorarchdir}/%%{ruby25_sitearchdir}.
#
# Note that this must be invoked in the spec file, preferably as
# "%{?ruby25_default_filter}", before any %description block.
%ruby25_default_filter %{expand: \
%global __provides_exclude_from %{?__provides_exclude_from:%{__provides_exclude_from}|}^(%{ruby25_vendorarchdir}|%{ruby25_sitearchdir})/.*\\\\.so$ \
}
