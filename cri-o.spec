%global debug_package %{nil}

Name: cri-o
Epoch: 100
Version: 1.21.4
Release: 1%{?dist}
Summary: OCI-based implementation of Kubernetes Container Runtime Interface
License: Apache-2.0
URL: https://github.com/cri-o/cri-o/tags
Source0: %{name}_%{version}.orig.tar.gz
%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
BuildRequires: timezone
%else
BuildRequires: tzdata
%endif
BuildRequires: golang-1.17
BuildRequires: glibc-static
BuildRequires: glib2-devel
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libgpg-error-devel
BuildRequires: libseccomp-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-devel
%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
Requires: timezone
%else
Requires: tzdata
%endif
Requires: conmon
Requires: conntrack-tools
Requires: containernetworking-plugins
Requires: containers-common
Requires: iproute
Requires: iptables
Requires: oci-runtime
Requires: socat

%description
CRI-O provides an integration path between OCI conformant runtimes and
the kubelet. Specifically, it implements the Kubelet Container Runtime
Interface (CRI) using OCI conformant runtimes. The scope of CRI-O is
tied to the scope of the CRI.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
mkdir -p bin
set -ex && \
    export CGO_ENABLED=1 && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp selinux" \
        -o ./bin/crio ./cmd/crio && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp selinux" \
        -o ./bin/crio-status ./cmd/crio-status && \
    make bin/pinns
./bin/crio -d "" --config="" \
    --cni-plugin-dir "/usr/libexec/cni" \
    --cni-plugin-dir "/usr/lib/cni" \
    --cni-plugin-dir "/opt/cni/bin" \
    --conmon-env "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
    --conmon-env "TERM=xterm" \
    --default-capabilities "AUDIT_WRITE" \
    --default-capabilities "CHOWN" \
    --default-capabilities "DAC_OVERRIDE" \
    --default-capabilities "FOWNER" \
    --default-capabilities "FSETID" \
    --default-capabilities "KILL" \
    --default-capabilities "MKNOD" \
    --default-capabilities "NET_BIND_SERVICE" \
    --default-capabilities "NET_RAW" \
    --default-capabilities "SETFCAP" \
    --default-capabilities "SETGID" \
    --default-capabilities "SETPCAP" \
    --default-capabilities "SETUID" \
    --default-capabilities "SYS_CHROOT" \
    --pause-image "k8s.gcr.io/pause:3.5" \
    --root "/var/lib/containers/storage" \
    --runroot "/run/containers/storage" \
    --seccomp-profile "/usr/share/containers/seccomp.json" \
    config > crio.conf

%install
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/crio
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/crio-status
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/pinns
DESTDIR=%{buildroot} \
PREFIX=%{buildroot}%{_prefix} \
    make install.completions install.config-nobuild
PREFIX=%{buildroot}%{_prefix} \
        make install.systemd

%files
%license LICENSE
%dir %{_sysconfdir}/crio
%dir %{_sysconfdir}/crio/crio.conf.d
%dir %{_datadir}/containers
%dir %{_datadir}/containers/oci
%dir %{_datadir}/containers/oci/hooks.d
%dir %{_datadir}/fish
%dir %{_datadir}/fish/completions
%dir %{_datadir}/oci-umount
%dir %{_datadir}/oci-umount/oci-umount.d
%{_bindir}/crio
%{_bindir}/crio-status
%{_bindir}/pinns
%{_datadir}/bash-completion/completions/crio
%{_datadir}/bash-completion/completions/crio-status
%{_datadir}/fish/completions/crio-status.fish
%{_datadir}/fish/completions/crio.fish
%{_datadir}/oci-umount/oci-umount.d/crio-umount.conf
%{_datadir}/zsh/site-functions/_crio
%{_datadir}/zsh/site-functions/_crio-status
%{_sysconfdir}/crictl.yaml
%{_sysconfdir}/crio/crio.conf
%{_unitdir}/cri-o.service
%{_unitdir}/crio-shutdown.service
%{_unitdir}/crio-wipe.service
%{_unitdir}/crio.service

%changelog
