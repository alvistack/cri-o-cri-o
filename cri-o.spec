# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

Name: cri-o
Epoch: 100
Version: 1.23.1
Release: 3%{?dist}
Summary: OCI-based implementation of Kubernetes Container Runtime Interface
License: Apache-2.0
URL: https://github.com/cri-o/cri-o/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: glib2-devel
BuildRequires: glibc-static
BuildRequires: golang-1.17
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libgpg-error-devel
BuildRequires: libseccomp-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-devel
BuildRequires: tzdata
Requires: conmon
Requires: conntrack-tools
Requires: containernetworking-plugins
Requires: containers-common
Requires: iproute
Requires: iptables
Requires: oci-runtime
Requires: socat
Requires: tzdata

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
    --cni-plugin-dir "/usr/local/libexec/cni" \
    --cni-plugin-dir "/usr/libexec/cni" \
    --cni-plugin-dir "/usr/local/lib/cni" \
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
    --pause-image "registry.k8s.io/pause:3.6" \
    --root "/var/lib/containers/storage" \
    --runroot "/run/containers/storage" \
    --seccomp-profile "/usr/share/containers/seccomp.json" \
    config > crio.conf

%install
install -Dpm755 -d %{buildroot}%{_sysconfdir}/cni/net.d
install -Dpm755 -d %{buildroot}%{_sysconfdir}/default
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm644 -T contrib/cni/11-crio-ipv4-bridge.conf %{buildroot}%{_sysconfdir}/cni/net.d/87-crio-bridge.conf
install -Dpm644 -T contrib/sysconfig/crio %{buildroot}%{_sysconfdir}/default/crio
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
%dir %{_sysconfdir}/cni
%dir %{_sysconfdir}/cni/net.d
%dir %{_sysconfdir}/crio
%dir %{_sysconfdir}/crio/crio.conf.d
%dir %{_sysconfdir}/default
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
%{_sysconfdir}/cni/net.d/87-crio-bridge.conf
%{_sysconfdir}/crictl.yaml
%{_sysconfdir}/crio/crio.conf
%{_sysconfdir}/default/crio
%{_unitdir}/crio-wipe.service
%{_unitdir}/crio.service

%changelog
