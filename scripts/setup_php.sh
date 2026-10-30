#!/usr/bin/env bash
# Optional native-verification runtime for the managed Debian 13 amd64 image.
# Installs into an isolated directory without root, Composer, or system changes.
# Core Python reproduction does not need PHP or this script.
set -euo pipefail

. /etc/os-release
if [[ "${ID:-}" != debian || "${VERSION_ID:-}" != 13 || "$(dpkg --print-architecture)" != amd64 ]]; then
    printf '%s\n' 'This helper supports Debian 13 amd64 only. Install a trusted PHP CLI using your platform package manager.' >&2
    exit 1
fi
for executable in /usr/bin/apt-get dpkg-deb sha256sum; do
    command -v "$executable" >/dev/null
done
test -r /usr/share/keyrings/debian-archive-keyring.gpg

runtime_dir="${1:-/workspace/tools/php}"
mkdir -p "$runtime_dir"
runtime_dir="$(cd "$runtime_dir" && pwd -P)"
package_dir="${runtime_dir}-packages"
apt_dir="${runtime_dir}-apt"
mkdir -p "$package_dir" "$apt_dir/lists/partial" "$apt_dir/cache/archives/partial" "$apt_dir/empty"

cat > "$apt_dir/sources.list" <<'SOURCES'
deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] https://deb.debian.org/debian trixie main
deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] https://security.debian.org/debian-security trixie-security main
SOURCES

# Read only these local APT settings; do not invoke system package-manager hooks.
# No proxy addresses or credentials are written to configuration files.
cat > "$apt_dir/apt.conf" <<CONFIG
Dir::Etc::main "/dev/null";
Dir::Etc::parts "$apt_dir/empty";
Dir::Etc::sourcelist "$apt_dir/sources.list";
Dir::Etc::sourceparts "$apt_dir/empty";
Dir::State::lists "$apt_dir/lists";
Dir::Cache "$apt_dir/cache";
APT::Sandbox::User "$(id -un)";
CONFIG

# Preserve the session proxy and TLS trust. APT expects lowercase proxy variables.
run_apt() {
    APT_CONFIG="$apt_dir/apt.conf" \
    http_proxy="${HTTP_PROXY:-${http_proxy:-}}" \
    https_proxy="${HTTPS_PROXY:-${https_proxy:-}}" \
    /usr/bin/apt-get "$@"
}

run_apt update
(
    cd "$package_dir"
    # Versions and hashes were authenticated against signed Debian metadata on
    # 2026-10-30. An unavailable version or any byte mismatch fails visibly.
    run_apt download php8.4-cli=8.4.27-1~deb13u1 libargon2-1=0~20190702+dfsg-4+b2
    sha256sum --check <<'CHECKSUMS'
111191e9eec53db65198f9a38a15dcbd498935be88e2fa83336ba142fd5ae152  php8.4-cli_8.4.27-1~deb13u1_amd64.deb
a54a6640be69c29c1e43b14ee464484a6f20e33fe73200c02949cfeb03228547  libargon2-1_0~20190702+dfsg-4+b2_amd64.deb
CHECKSUMS
    dpkg-deb -x php8.4-cli_8.4.27-1~deb13u1_amd64.deb "$runtime_dir"
    dpkg-deb -x libargon2-1_0~20190702+dfsg-4+b2_amd64.deb "$runtime_dir"
)

mkdir -p "$runtime_dir/bin"
cat > "$runtime_dir/bin/php" <<'WRAPPER'
#!/bin/sh
runtime_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
exec /lib64/ld-linux-x86-64.so.2 --library-path "$runtime_dir/usr/lib/x86_64-linux-gnu" "$runtime_dir/usr/bin/php8.4" "$@"
WRAPPER
chmod 755 "$runtime_dir/bin/php"
"$runtime_dir/bin/php" -n -v
printf 'PHP executable: %s/bin/php\n' "$runtime_dir"
