%define patchleveltag .37
%define baseversion 5.2

Version: %{baseversion}%{patchleveltag}
Name: gnu-bash
Summary: The GNU Bourne Again shell
Release: 0
License: GPLv3+
Url: https://git.sailfishos.org/mer-core/bash
Source0: %{name}-%{version}.tar.gz
Source1: dot-bashrc
Source2: dot-bash_profile
Source3: dot-bash_logout

Obsoletes: bash < 1:3.2.57+git1
Provides: bash = 1:3.2.57+git1

# Other patches from Fedora
# Non-interactive shells beginning with argv[0][0] == '-' should run the startup files when not in posix mode.
Patch102: bash-2.03-profile.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=60870
Patch103: bash-2.05a-interpreter.patch
# Generate info for debuginfo files.
Patch104: bash-2.05b-debuginfo.patch
# Pid passed to setpgrp() can not be pid of a zombie process.
Patch105: bash-2.05b-pgrp_sync.patch
# Source bashrc file when bash is run under ssh.
Patch107: bash-3.2-ssh_source_bash.patch
# Use makeinfo to generate .texi file
# Patch108: bash-infotags.patch
# Try to pick up latest `--rpm-requires` patch from http://git.altlinux.org/gears/b/bash4.git
Patch109: bash-requires.patch
Patch110: bash-setlocale.patch
# Disable tty tests while doing bash builds
Patch111: bash-tty-tests.patch

# 484809, check if interp section is NOBITS
Patch116: bash-4.0-nobits.patch

# Do the same CFLAGS in generated Makefile in examples
Patch117: bash-4.1-examples.patch

# Builtins like echo and printf won't report errors
# when output does not succeed due to EPIPE
Patch118: bash-4.1-broken_pipe.patch

# Enable system-wide .bash_logout for login shells
Patch119: bash-4.2-rc2-logout.patch

# Static analyzis shows some issues in bash-2.05a-interpreter.patch
Patch120: bash-4.2-coverity.patch

# 799958, updated info about trap
# This patch should be upstreamed.
Patch122: bash-4.2-manpage_trap.patch

# https://www.securecoding.cert.org/confluence/display/seccode/INT32-C.+Ensure+that+operations+on+signed+integers+do+not+result+in+overflow
# This patch should be upstreamed.
Patch123: bash-4.2-size_type.patch

# 1112710 - mention ulimit -c and -f POSIX block size
# This patch should be upstreamed.
Patch124: bash-4.3-man-ulimit.patch

# 1102815 - fix double echoes in vi visual mode
Patch125: bash-4.3-noecho.patch

#1241533,1224855 - bash leaks memory when LC_ALL set
Patch126: bash-4.3-memleak-lc_all.patch

# bash-4.4 builds loadable builtin examples by default
# this patch disables it
Patch127: bash-4.4-no-loadable-builtins.patch

# 2020528 - Add a runtime option to enable history logging to syslog
# This option is undocumented in upstream and is documented by this patch
Patch128: bash-5.0-syslog-history.patch
Patch129: bash-configure-c99.patch

# Enable audit logs
Patch131: bash-4.3-audit.patch

# Fixes for issues found by OpenScanHub
Patch132: bash-5.3-sast.patch

BuildRequires: texinfo bison
BuildRequires: ncurses-devel
BuildRequires: autoconf, gettext
BuildRequires: audit-libs-devel

%description
The GNU Bourne Again shell (Bash) is a shell or command language
interpreter that is compatible with the Bourne shell (sh). Bash
incorporates useful features from the Korn shell (ksh) and the C shell
(csh). Most sh scripts can be run by bash without modification.

%package doc
Summary: Documentation files for %{name}
Requires: %{name} = %{version}-%{release}

%description doc
This package contains documentation files for %{name}.

%define _pkgdocdir %{_docdir}/%{name}-%{version}

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
autoconf
%configure --with-bash-malloc=no --with-afs --docdir="%{_pkgdocdir}"

# Recycles pids is neccessary. When bash's last fork's pid was X
# and new fork's pid is also X, bash has to wait for this same pid.
# Without Recycles pids bash will not wait.
make "CPPFLAGS=-D_GNU_SOURCE -DRECYCLES_PIDS -DDEFAULT_PATH_VALUE='\"/usr/local/bin:/usr/bin:/bin\"' `getconf LFS_CFLAGS`" %{?_smp_mflags}

%install

if [ -e autoconf ]; then
  # Yuck. We're using autoconf 2.1x.
  export PATH=.:$PATH
fi

# Fix bug #83776
sed -i -e 's,bashref\.info,bash.info,' doc/bashref.info

%make_install

mkdir -p %{buildroot}%{_sysconfdir}

# make manpages for bash builtins as per suggestion in DOC/README
pushd doc
sed -e '
/^\.SH NAME/, /\\- bash built-in commands, see \\fBbash\\fR(1)$/{
/^\.SH NAME/d
s/^bash, //
s/\\- bash built-in commands, see \\fBbash\\fR(1)$//
s/,//g
b
}
d
' builtins.1 > man.pages
for i in echo pwd test kill; do
  sed -i -e "s,$i,,g" man.pages
  sed -i -e "s,  , ,g" man.pages
done

install -c -m 644 builtins.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/builtins.1

for i in `cat man.pages` ; do
  echo .so man1/builtins.1 > ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
  chmod 0644 ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
done
popd

# Link bash man page to sh so that man sh works.
ln -s bash.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/sh.1

# Not for printf, true and false (conflict with coreutils)
rm -f %{buildroot}/%{_mandir}/man1/printf.1
rm -f %{buildroot}/%{_mandir}/man1/true.1
rm -f %{buildroot}/%{_mandir}/man1/false.1

# Legacy paths
mkdir -p %{buildroot}/bin
ln -sf ../usr/bin/bash %{buildroot}/bin/bash
ln -sf ../usr/bin/bash %{buildroot}/bin/sh
# bash as sh
ln -sf bash %{buildroot}%{_bindir}/sh
# other stuff
rm -f %{buildroot}%{_infodir}/dir
mkdir -p %{buildroot}%{_sysconfdir}/skel
install -p -m644 %SOURCE1 %{buildroot}%{_sysconfdir}/skel/.bashrc
install -p -m644 %SOURCE2 %{buildroot}%{_sysconfdir}/skel/.bash_profile
install -p -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/skel/.bash_logout
rm -f %{buildroot}%{_bindir}/bashbug

# Fix missing sh-bangs in example scripts (bug #225609).
for script in \
  examples/scripts/shprompt
  # there used to be more here
do
  cp "$script" "$script"-orig
  echo '#!/bin/bash' > "$script"
  cat "$script"-orig >> "$script"
  rm -f "$script"-orig
done

%find_lang bash
mv bash.lang %{name}.lang

# copy doc to /usr/share/doc/
mkdir -p %{buildroot}/%{_pkgdocdir}
for file in CHANGES COMPAT NEWS NOTES POSIX RBASH README examples \
            doc/*.ps doc/*.0 doc/article.txt
do
  cp -rp "$file" %{buildroot}/%{_pkgdocdir}/"${file##doc/}"
done
# loadables aren't buildable
rm -rf "%{buildroot}/%{_pkgdocdir}/examples/loadables"

%lang_package

# ***** bash doesn't use install-info. It's always listed in %%{_infodir}/dir
# to prevent prereq loops

%files
%license COPYING
%config %{_sysconfdir}/skel/.b*
/bin/sh
/bin/bash
%{_bindir}/sh
%{_bindir}/bash

%files doc
%{_pkgdocdir}
%{_infodir}/bash.*
%{_mandir}/man1/..1.*
%{_mandir}/man*/*
