#!/bin/bash
# HireMeBahamas - Dependency Status Checker
# This script checks the status of all required dependencies using apt-get

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "================================================================"
echo -e "${BLUE}  HireMeBahamas - APT-GET Dependency Status Check${NC}"
echo "================================================================"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${CYAN}━━━ $1 ━━━${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check if package is installed and get version
check_package() {
    local package=$1
    local description=$2
    
    if dpkg -l "$package" 2>/dev/null | grep -q "^ii"; then
        # Package is installed, get version
        version=$(dpkg -l "$package" 2>/dev/null | grep "^ii" | awk '{print $3}')
        print_success "$description ($package) - v$version"
        return 0
    else
        print_error "$description ($package) - NOT INSTALLED"
        return 1
    fi
}

# Function to check command availability
check_command() {
    local cmd=$1
    local description=$2
    
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | head -n1)
        print_success "$description: $version"
        return 0
    else
        print_error "$description: NOT FOUND"
        return 1
    fi
}

# Tracking variables
TOTAL_PACKAGES=0
INSTALLED_PACKAGES=0
MISSING_PACKAGES=()

# 1. Build Tools
print_section "1. Build Tools"
for pkg in "build-essential:Build Essential" "gcc:GCC Compiler" "g++:G++ Compiler" "make:Make Build Tool" "pkg-config:Package Config"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 2. Python Dependencies
print_section "2. Python Dependencies"
for pkg in "python3:Python 3" "python3-pip:Python pip" "python3-dev:Python Dev Headers" "python3-venv:Python Virtual Env"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 3. Database Dependencies
print_section "3. Database Dependencies"
for pkg in "postgresql:PostgreSQL Server" "postgresql-client:PostgreSQL Client" "libpq-dev:PostgreSQL Dev Libraries"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 4. Redis Cache
print_section "4. Redis Cache & Message Broker"
for pkg in "redis-server:Redis Server" "redis-tools:Redis Tools"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 5. SSL/Crypto Libraries
print_section "5. SSL/Crypto Libraries"
for pkg in "libssl-dev:OpenSSL Dev Library" "libffi-dev:FFI Dev Library"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 6. Image Processing Libraries
print_section "6. Image Processing Libraries"
for pkg in "libjpeg-dev:JPEG Library" "libpng-dev:PNG Library"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 7. Additional Libraries
print_section "7. Additional Libraries"
for pkg in "libevent-dev:Event Library" "libxml2-dev:XML2 Library" "libxslt1-dev:XSLT Library"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 8. Web Server
print_section "8. Web Server"
TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
if check_package "nginx" "Nginx Web Server"; then
    INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
else
    MISSING_PACKAGES+=("nginx")
fi

# 9. Utilities
print_section "9. Essential Utilities"
for pkg in "curl:cURL" "wget:wget" "git:Git"; do
    IFS=':' read -r package description <<< "$pkg"
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if check_package "$package" "$description"; then
        INSTALLED_PACKAGES=$((INSTALLED_PACKAGES + 1))
    else
        MISSING_PACKAGES+=("$package")
    fi
done

# 10. Check runtime commands
print_section "10. Runtime Commands"
check_command "python3" "Python 3"
check_command "pip" "pip Package Manager"
check_command "node" "Node.js"
check_command "npm" "npm Package Manager"
check_command "psql" "PostgreSQL Client"
check_command "redis-cli" "Redis CLI"

# 11. Check Services Status
print_section "11. Services Status"

# Check PostgreSQL
if systemctl is-active --quiet postgresql 2>/dev/null; then
    print_success "PostgreSQL Service: RUNNING"
elif systemctl status postgresql &>/dev/null; then
    status=$(systemctl is-active postgresql 2>/dev/null)
    print_warning "PostgreSQL Service: $status"
else
    print_warning "PostgreSQL Service: Not configured or not using systemd"
fi

# Check Redis
if systemctl is-active --quiet redis-server 2>/dev/null; then
    print_success "Redis Service: RUNNING"
elif systemctl status redis-server &>/dev/null; then
    status=$(systemctl is-active redis-server 2>/dev/null)
    print_warning "Redis Service: $status"
else
    print_warning "Redis Service: Not configured or not using systemd"
fi

# 12. Check disk space for apt cache
print_section "12. APT Cache Information"
apt_cache_size=$(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1 || echo "Unknown")
echo -e "${CYAN}APT Cache Size:${NC} $apt_cache_size"

# Check if apt-get update is needed
last_update=$(stat -c %Y /var/lib/apt/periodic/update-success-stamp 2>/dev/null || echo "0")
current_time=$(date +%s)
days_since_update=$(( (current_time - last_update) / 86400 ))
if [ "$days_since_update" -gt 7 ]; then
    print_warning "Package lists last updated $days_since_update days ago (consider running 'sudo apt-get update')"
else
    print_success "Package lists are up to date (last updated $days_since_update days ago)"
fi

# Summary
echo ""
echo "================================================================"
echo -e "${BLUE}                    SUMMARY${NC}"
echo "================================================================"
echo ""

PERCENTAGE=$((INSTALLED_PACKAGES * 100 / TOTAL_PACKAGES))

echo -e "${CYAN}Total Packages Checked:${NC}    $TOTAL_PACKAGES"
echo -e "${GREEN}Installed Packages:${NC}        $INSTALLED_PACKAGES"
if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo -e "${GREEN}Missing Packages:${NC}          0"
else
    echo -e "${RED}Missing Packages:${NC}          ${#MISSING_PACKAGES[@]}"
fi
echo -e "${CYAN}Installation Progress:${NC}     ${PERCENTAGE}%"

# Progress bar
BAR_LENGTH=50
FILLED=$((PERCENTAGE * BAR_LENGTH / 100))
EMPTY=$((BAR_LENGTH - FILLED))
echo -n "["
for ((i=0; i<FILLED; i++)); do echo -n "█"; done
for ((i=0; i<EMPTY; i++)); do echo -n "░"; done
echo "] ${PERCENTAGE}%"

echo ""

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required packages are installed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Install Python packages: pip install -r requirements.txt"
    echo "  2. Install frontend packages: cd frontend && npm install"
    echo "  3. Run tests: python test_app_operational.py"
    exit 0
else
    echo -e "${RED}✗ Some packages are missing!${NC}"
    echo ""
    echo "Missing packages:"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo "  - $pkg"
    done
    echo ""
    echo "To install missing packages, run:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y ${MISSING_PACKAGES[@]}"
    echo ""
    echo "Or run the complete installation script:"
    echo "  ./install_dependencies.sh"
    exit 1
fi
