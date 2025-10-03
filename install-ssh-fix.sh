#!/bin/bash
#############################################################
# SSH Installation Fix Script
# This script handles SSH server installation without hanging
#############################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info "Installing SSH server with conflict resolution..."

# Method 1: Pre-configure and install
export DEBIAN_FRONTEND=noninteractive
export UCF_FORCE_CONFFNEW=1

# Pre-configure SSH server to keep existing configuration
echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true
echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true

# Try installation with timeout
if timeout 300 bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get install -y -qq --no-install-recommends openssh-server'; then
    print_success "SSH server installed successfully"
    exit 0
fi

print_error "SSH server installation failed, trying alternative approach..."

# Method 2: Try with dpkg directly
print_info "Trying dpkg approach..."
if timeout 300 bash -c 'export DEBIAN_FRONTEND=noninteractive; dpkg --configure -a; apt-get install -y -qq --no-install-recommends openssh-server'; then
    print_success "SSH server installed successfully"
    exit 0
fi

print_error "SSH server installation failed, trying final approach..."

# Method 3: Try with force and ignore errors
print_info "Trying force installation..."
timeout 300 bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get install -y -qq --no-install-recommends openssh-server --force-yes' || {
    print_error "SSH server installation failed, but continuing..."
    exit 1
}

print_success "SSH server installed successfully"
