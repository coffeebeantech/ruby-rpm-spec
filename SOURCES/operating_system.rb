module Gem
  class << self
    ##
    # Default gems locations allowed on FHS system (/usr, /usr/share).
    # The locations are derived from directories specified during build
    # configuration.

    # rubygems defines the gem installation location location based off of
    # vendorlibdir and sitelibdir which were defined during build. The only
    # difference is instead of vendor_ruby or site_ruby the directory gems is used
    def default_locations
      @default_locations ||= {
        :system => ConfigMap[:vendorlibdir].gsub(/vendor_ruby/, "gems"),
        :local => ConfigMap[:sitelibdir].gsub(/site_ruby/, "gems")
      }
    end

    ##
    # For each location provides set of directories for binaries (:bin_dir)
    # platform independent (:gem_dir) and dependent (:ext_dir) files.

    def default_dirs
      @libdir ||= case RUBY_PLATFORM
      when 'java'
        ConfigMap[:datadir]
      else
        ConfigMap[:libdir]
      end

      @default_dirs ||= Hash[default_locations.collect do |destination, path|
        [destination, {
           # The proper bin directory for the :system and :local is always four levels above path
          :bin_dir => File.realdirpath(File.join(path, [ ".." ] * 4, ConfigMap[:bindir].split(File::SEPARATOR).last)),
          :gem_dir => path,
           # The only difference between path and ext_dir is instead of share we need to look in lib/lib64 the rest
           # of the path is the same
          :ext_dir => File.join(path.gsub(/share/, @libdir.split(File::SEPARATOR).last), "gems")
        }]
      end]
    end

    ##
    # Remove methods we are going to override. This avoids "method redefined;"
    # warnings otherwise issued by Ruby.

    remove_method :default_dir if method_defined? :default_dir
    remove_method :default_path if method_defined? :default_path
    remove_method :default_bindir if method_defined? :default_bindir
    remove_method :default_ext_dir_for if method_defined? :default_ext_dir_for

    ##
    # RubyGems default overrides.

    def default_dir
      if Process.uid == 0
        Gem.default_dirs[:local][:gem_dir]
      else
        Gem.user_dir
      end
    end

    def default_path
      path = default_dirs.collect {|location, paths| paths[:gem_dir]}
      path.unshift Gem.user_dir if File.exist? Gem.user_home
    end

    def default_bindir
      if Process.uid == 0
        Gem.default_dirs[:local][:bin_dir]
      else
        File.join [Dir.home, 'bin']
      end
    end

    def default_ext_dir_for base_dir
      dirs = Gem.default_dirs.detect {|location, paths| paths[:gem_dir] == base_dir}
      dirs && dirs.last[:ext_dir]
    end

    # This method should be available since RubyGems 2.2 until RubyGems 3.0.
    # https://github.com/rubygems/rubygems/issues/749
    if method_defined? :install_extension_in_lib
      remove_method :install_extension_in_lib

      def install_extension_in_lib
        false
      end
    end
  end
end
