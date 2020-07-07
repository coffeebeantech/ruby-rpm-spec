# What is this spec?

This spec is an attempt to keep Ruby updated to the latest stable version available and to be used on [Amazon Linux AMI](https://aws.amazon.com/amazon-linux-ami/).

It specifies a new set of Ruby RPMs using a suffix, like ruby25-2.5.8-1.0.1.amzn1.x86_64.rpm (and executables ruby2.5). It allows to install a new ruby version keeping old versions running at the same time.

# What is the current version?

Ruby 2.5.8

# How to build?

Move the repository contents for an directory like that:

    /home/ec2-user/packaging/ruby-rpm-spec

And run rpmbuild:

    cd /home/ec2-user/packaging/ruby-rpm-spec && rm -rf BUILDROOT/* BUILD/* RPMS/x86_64/* RPMS/noarch/* && cd SPECS/ && rpmbuild -ba --buildroot=/home/ec2-user/packaging/ruby-rpm-spec/BUILDROOT --define='_topdir /home/ec2-user/packaging/ruby-rpm-spec' --sign ruby25.spec

**Important**: if you try to rebuild the spec with the generated ruby and rubygems RPMs already installed on the system, you'll get and error regarding the gems directory. In this case, you need first to remove the RPMs and then build and install the new ones. There is some compatibility issue building this spec with the packages already installed. If you know why please tell me :)

# How to install?

    sudo rpm -ivh noarch/rubygem25-rdoc-6.0.1.1-1.0.1.amzn1.noarch.rpm x86_64/* noarch/rubygems25-2.7.6.2-1.0.1.amzn1.noarch.rpm noarch/ruby25-irb-2.5.8-1.0.1.amzn1.noarch.rpm

# Sources

This spec is based on Fedora's spec available on http://pkgs.fedoraproject.org/cgit/ruby.git/.

Also, it has been used the spec of the latest ruby rpm available on Amazon's repositories.
