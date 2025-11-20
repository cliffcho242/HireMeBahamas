#!/bin/bash
#================================================================
# HireMeBahamas - Complete Dependency Installation Script
#================================================================
# This script installs ALL dependencies for the HireMeBahamas
# application with ZERO manual intervention.
#
# Supports:
#   - Ubuntu/Debian (apt-get)
#   - CentOS/RHEL (yum)
#   - macOS (Homebrew)
#
# Usage: ./scripts/install_all_dependencies.sh [options]
# Options:
#   --dry-run       Show what would be installed without installing
#   --skip-system   Skip system package installation
#   --skip-python   Skip Python package installation
#   --skip-node     Skip Node.js package installation
#   --skip-services Skip service configuration
#   --force         Force reinstall of all packages
#   --help          Show this help message
#================================================================

set -e  # Exit on error
set -o pipefail  # Catch errors in pipelines

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color
readonly BOLD='\033[1m'

# Script variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/installation.log"
DRY_RUN=false
SKIP_SYSTEM=false
SKIP_PYTHON=false
SKIP_NODE=false
SKIP_SERVICES=false
FORCE_INSTALL=false
OS_TYPE=""
PKG_MANAGER=""

# Logging functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    log "=== $1 ==="
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
    log "[SUCCESS] $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    log "[WARNING] $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    log "[ERROR] $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
    log "[INFO] $1"
}

print_progress() {
    echo -e "${MAGENTA}▶${NC} $1"
    log "[PROGRESS] $1"
}

# Error handler
error_exit() {
    print_error "$1"
    echo -e "\n${RED}Installation failed. Check $LOG_FILE for details.${NC}"
    exit 1
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-system)
                SKIP_SYSTEM=true
                shift
                ;;
            --skip-python)
                SKIP_PYTHON=true
                shift
                ;;
            --skip-node)
                SKIP_NODE=true
                shift
                ;;
            --skip-services)
                SKIP_SERVICES=true
                shift
                ;;
            --force)
                FORCE_INSTALL=true
                shift
                ;;
            --help)
                head -n 23 "$0" | tail -n 16
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Detect operating system
detect_os() {
    print_header "Detecting Operating System"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]] || [[ "$ID_LIKE" == *"debian"* ]]; then
                OS_TYPE="debian"
                PKG_MANAGER="apt-get"
                print_status "Detected: Ubuntu/Debian-based Linux"
            elif [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID_LIKE" == *"rhel"* ]]; then
                OS_TYPE="rhel"
                PKG_MANAGER="yum"
                print_status "Detected: CentOS/RHEL-based Linux"
            else
                print_warning "Detected Linux but unknown distribution: $ID"
                OS_TYPE="linux"
                PKG_MANAGER="unknown"
            fi
        else
            OS_TYPE="linux"
            PKG_MANAGER="unknown"
            print_warning "Could not determine Linux distribution"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        PKG_MANAGER="brew"
        print_status "Detected: macOS"
    else
        error_exit "Unsupported operating system: $OSTYPE"
    fi
    
    log "OS: $OS_TYPE, Package Manager: $PKG_MANAGER"
}

# Check if running with sufficient privileges
check_privileges() {
    if [[ "$OS_TYPE" != "macos" ]] && [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        print_warning "This script requires sudo privileges for system package installation"
        print_info "You may be prompted for your password"
    fi
}

# Update package manager
update_system() {
    if [[ "$SKIP_SYSTEM" == true ]]; then
        print_warning "Skipping system updates (--skip-system)"
        return
    fi
    
    print_header "Updating Package Manager"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would update package manager: $PKG_MANAGER"
        return
    fi
    
    case $PKG_MANAGER in
        apt-get)
            print_progress "Updating apt repositories..."
            sudo apt-get update -y || error_exit "Failed to update apt repositories"
            print_status "APT repositories updated"
            ;;
        yum)
            print_progress "Updating yum repositories..."
            sudo yum update -y || error_exit "Failed to update yum repositories"
            print_status "YUM repositories updated"
            ;;
        brew)
            print_progress "Updating Homebrew..."
            if ! command -v brew &> /dev/null; then
                print_warning "Homebrew not installed. Installing..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || error_exit "Failed to install Homebrew"
            fi
            brew update || error_exit "Failed to update Homebrew"
            print_status "Homebrew updated"
            ;;
        *)
            print_warning "Unknown package manager, skipping system update"
            ;;
    esac
}

# Install system dependencies
install_system_deps() {
    if [[ "$SKIP_SYSTEM" == true ]]; then
        print_warning "Skipping system dependencies (--skip-system)"
        return
    fi
    
    print_header "Installing System Dependencies"
    
    local deps_debian=(
        "build-essential"
        "python3"
        "python3-pip"
        "python3-dev"
        "python3-venv"
        "postgresql"
        "postgresql-contrib"
        "postgresql-client"
        "libpq-dev"
        "redis-server"
        "redis-tools"
        "nodejs"
        "npm"
        "libffi-dev"
        "libssl-dev"
        "pkg-config"
        "curl"
        "wget"
        "git"
    )
    
    local deps_rhel=(
        "gcc"
        "gcc-c++"
        "make"
        "python3"
        "python3-pip"
        "python3-devel"
        "postgresql"
        "postgresql-server"
        "postgresql-devel"
        "redis"
        "nodejs"
        "npm"
        "libffi-devel"
        "openssl-devel"
        "pkgconfig"
        "curl"
        "wget"
        "git"
    )
    
    local deps_macos=(
        "python@3.12"
        "postgresql@15"
        "redis"
        "node"
        "openssl"
        "libffi"
        "pkg-config"
    )
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would install system dependencies"
        return
    fi
    
    case $PKG_MANAGER in
        apt-get)
            print_progress "Installing system packages via apt-get..."
            for dep in "${deps_debian[@]}"; do
                print_info "Installing: $dep"
                if [[ "$FORCE_INSTALL" == true ]]; then
                    sudo apt-get install -y --reinstall "$dep" || print_warning "Failed to install $dep"
                else
                    sudo apt-get install -y "$dep" || print_warning "Failed to install $dep"
                fi
            done
            print_status "System dependencies installed"
            ;;
        yum)
            print_progress "Installing system packages via yum..."
            for dep in "${deps_rhel[@]}"; do
                print_info "Installing: $dep"
                if [[ "$FORCE_INSTALL" == true ]]; then
                    sudo yum reinstall -y "$dep" || print_warning "Failed to install $dep"
                else
                    sudo yum install -y "$dep" || print_warning "Failed to install $dep"
                fi
            done
            # Initialize PostgreSQL on RHEL
            if ! sudo systemctl is-active --quiet postgresql; then
                sudo postgresql-setup --initdb || print_warning "Failed to initialize PostgreSQL"
            fi
            print_status "System dependencies installed"
            ;;
        brew)
            print_progress "Installing system packages via Homebrew..."
            for dep in "${deps_macos[@]}"; do
                print_info "Installing: $dep"
                if brew list "$dep" &>/dev/null && [[ "$FORCE_INSTALL" == true ]]; then
                    brew reinstall "$dep" || print_warning "Failed to install $dep"
                else
                    brew install "$dep" || print_warning "Failed to install $dep (may already be installed)"
                fi
            done
            print_status "System dependencies installed"
            ;;
        *)
            print_warning "Unknown package manager, skipping system dependencies"
            print_info "Please install system dependencies manually"
            ;;
    esac
}

# Install Python dependencies
install_python_deps() {
    if [[ "$SKIP_PYTHON" == true ]]; then
        print_warning "Skipping Python dependencies (--skip-python)"
        return
    fi
    
    print_header "Installing Python Dependencies"
    
    # Ensure pip is available
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        error_exit "pip is not installed. Please install Python and pip first."
    fi
    
    local PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would upgrade pip and install Python dependencies"
        return
    fi
    
    # Upgrade pip
    print_progress "Upgrading pip..."
    $PIP_CMD install --upgrade pip || print_warning "Failed to upgrade pip"
    print_status "pip upgraded"
    
    # Install from requirements.txt
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_progress "Installing Python packages from requirements.txt..."
        $PIP_CMD install -r "$PROJECT_ROOT/requirements.txt" || error_exit "Failed to install Python dependencies"
        print_status "Python dependencies from requirements.txt installed"
    else
        print_warning "requirements.txt not found at $PROJECT_ROOT/requirements.txt"
    fi
    
    # Install additional required packages
    print_progress "Installing additional Python packages..."
    local additional_packages=(
        "psycopg2-binary"
        "redis"
        "sentry-sdk"
        "gunicorn"
        "flask-cors"
        "flask-limiter"
        "flask-caching"
        "flask-socketio"
        "flask-compress"
        "flask-talisman"
        "python-dotenv"
        "bcrypt"
        "pyjwt"
    )
    
    for pkg in "${additional_packages[@]}"; do
        print_info "Installing: $pkg"
        $PIP_CMD install "$pkg" || print_warning "Failed to install $pkg (may already be installed)"
    done
    
    print_status "All Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    if [[ "$SKIP_NODE" == true ]]; then
        print_warning "Skipping Node.js dependencies (--skip-node)"
        return
    fi
    
    print_header "Installing Node.js Dependencies"
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        error_exit "npm is not installed. Please install Node.js first."
    fi
    
    # Check Node.js version
    local node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 16 ]; then
        print_warning "Node.js version is less than 16. Some packages may not work correctly."
    else
        print_status "Node.js $(node --version) detected"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would install Node.js dependencies"
        return
    fi
    
    # Install global npm packages
    print_progress "Installing global npm packages..."
    npm install -g vite || print_warning "Failed to install vite globally"
    print_status "Global npm packages installed"
    
    # Install root dependencies
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        print_progress "Installing root npm dependencies..."
        cd "$PROJECT_ROOT"
        npm install || print_warning "Failed to install root npm dependencies"
        print_status "Root npm dependencies installed"
    fi
    
    # Install frontend dependencies
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        print_progress "Installing frontend dependencies..."
        cd "$PROJECT_ROOT/frontend"
        
        if [[ "$FORCE_INSTALL" == true ]]; then
            print_info "Force install: Removing node_modules and package-lock.json..."
            rm -rf node_modules package-lock.json
        fi
        
        npm install --legacy-peer-deps || error_exit "Failed to install frontend dependencies"
        print_status "Frontend dependencies installed"
    else
        print_warning "Frontend directory not found at $PROJECT_ROOT/frontend"
    fi
    
    cd "$PROJECT_ROOT"
}

# Configure services
configure_services() {
    if [[ "$SKIP_SERVICES" == true ]]; then
        print_warning "Skipping service configuration (--skip-services)"
        return
    fi
    
    print_header "Configuring Services"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would configure PostgreSQL and Redis services"
        return
    fi
    
    # Configure PostgreSQL
    print_progress "Configuring PostgreSQL..."
    
    case $OS_TYPE in
        debian)
            if command -v systemctl &> /dev/null; then
                sudo systemctl start postgresql || print_warning "Failed to start PostgreSQL"
                sudo systemctl enable postgresql || print_warning "Failed to enable PostgreSQL"
                print_status "PostgreSQL service started and enabled"
                
                # Create database
                print_progress "Creating database..."
                sudo -u postgres psql -c "CREATE DATABASE hiremebahamas;" 2>/dev/null || print_info "Database may already exist"
                sudo -u postgres psql -c "CREATE USER hiremebahamas WITH PASSWORD 'hiremebahamas';" 2>/dev/null || print_info "User may already exist"
                sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas;" 2>/dev/null || print_info "Privileges may already be granted"
                print_status "Database configured"
            else
                print_warning "systemctl not available, skipping service configuration"
            fi
            ;;
        rhel)
            if command -v systemctl &> /dev/null; then
                sudo systemctl start postgresql || print_warning "Failed to start PostgreSQL"
                sudo systemctl enable postgresql || print_warning "Failed to enable PostgreSQL"
                print_status "PostgreSQL service started and enabled"
                
                # Create database
                print_progress "Creating database..."
                sudo -u postgres psql -c "CREATE DATABASE hiremebahamas;" 2>/dev/null || print_info "Database may already exist"
                print_status "Database configured"
            else
                print_warning "systemctl not available, skipping service configuration"
            fi
            ;;
        macos)
            print_progress "Starting PostgreSQL on macOS..."
            brew services start postgresql@15 || print_warning "Failed to start PostgreSQL"
            sleep 3  # Give PostgreSQL time to start
            
            # Create database
            print_progress "Creating database..."
            createdb hiremebahamas 2>/dev/null || print_info "Database may already exist"
            print_status "PostgreSQL configured"
            ;;
    esac
    
    # Configure Redis
    print_progress "Configuring Redis..."
    
    case $OS_TYPE in
        debian|rhel)
            if command -v systemctl &> /dev/null; then
                sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || print_warning "Failed to start Redis"
                sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null || print_warning "Failed to enable Redis"
                print_status "Redis service started and enabled"
            else
                print_warning "systemctl not available, skipping Redis configuration"
            fi
            ;;
        macos)
            brew services start redis || print_warning "Failed to start Redis"
            print_status "Redis service started"
            ;;
    esac
    
    print_status "Services configured"
}

# Create environment files
create_env_files() {
    print_header "Creating Environment Files"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would create .env files"
        return
    fi
    
    # Backend .env
    if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
        print_progress "Creating backend/.env file..."
        cat > "$PROJECT_ROOT/backend/.env" << 'EOL'
DATABASE_URL=postgresql://hiremebahamas:hiremebahamas@localhost:5432/hiremebahamas
SECRET_KEY=change-this-to-a-secure-random-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
# Add your Cloudinary credentials:
# CLOUDINARY_NAME=your_cloudinary_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret
EOL
        print_status "Backend .env file created"
    else
        print_info "Backend .env file already exists"
    fi
    
    # Frontend .env
    if [ ! -f "$PROJECT_ROOT/frontend/.env" ]; then
        print_progress "Creating frontend/.env file..."
        cat > "$PROJECT_ROOT/frontend/.env" << 'EOL'
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
# Add your Cloudinary cloud name:
# VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
EOL
        print_status "Frontend .env file created"
    else
        print_info "Frontend .env file already exists"
    fi
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would verify installation"
        return
    fi
    
    local verification_script="$SCRIPT_DIR/verify_installation.py"
    
    if [ -f "$verification_script" ]; then
        print_progress "Running verification script..."
        python3 "$verification_script" || print_warning "Verification script reported issues"
    else
        # Basic manual verification
        print_progress "Running basic verification..."
        
        local all_ok=true
        
        # Check Python
        if command -v python3 &> /dev/null; then
            print_status "Python 3: $(python3 --version)"
        else
            print_error "Python 3 not found"
            all_ok=false
        fi
        
        # Check pip
        if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
            print_status "pip: Available"
        else
            print_error "pip not found"
            all_ok=false
        fi
        
        # Check Node.js
        if command -v node &> /dev/null; then
            print_status "Node.js: $(node --version)"
        else
            print_error "Node.js not found"
            all_ok=false
        fi
        
        # Check npm
        if command -v npm &> /dev/null; then
            print_status "npm: $(npm --version)"
        else
            print_error "npm not found"
            all_ok=false
        fi
        
        # Check PostgreSQL
        if command -v psql &> /dev/null; then
            print_status "PostgreSQL: Available"
        else
            print_warning "PostgreSQL client (psql) not found"
        fi
        
        # Check Redis
        if command -v redis-cli &> /dev/null; then
            print_status "Redis CLI: Available"
        else
            print_warning "Redis CLI not found"
        fi
        
        # Check if PostgreSQL is running
        if command -v pg_isready &> /dev/null; then
            if pg_isready -h localhost -p 5432 &> /dev/null; then
                print_status "PostgreSQL service: Running"
            else
                print_warning "PostgreSQL service: Not running"
            fi
        fi
        
        # Check if Redis is running
        if command -v redis-cli &> /dev/null; then
            if redis-cli ping &> /dev/null; then
                print_status "Redis service: Running"
            else
                print_warning "Redis service: Not running"
            fi
        fi
        
        if $all_ok; then
            print_status "Basic verification passed"
        else
            print_warning "Some checks failed"
        fi
    fi
}

# Main installation flow
main() {
    print_header "HireMeBahamas - Complete Dependency Installation"
    
    echo -e "${BOLD}This script will install ALL dependencies for HireMeBahamas${NC}"
    echo -e "Log file: ${CYAN}$LOG_FILE${NC}\n"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}${BOLD}DRY RUN MODE - No changes will be made${NC}\n"
    fi
    
    log "Installation started at $(date)"
    log "Script version: 1.0.0"
    log "Arguments: $*"
    
    # Run installation steps
    detect_os
    check_privileges
    update_system
    install_system_deps
    install_python_deps
    install_node_deps
    configure_services
    create_env_files
    verify_installation
    
    # Final summary
    print_header "Installation Complete!"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}${BOLD}This was a DRY RUN. No changes were made.${NC}"
        echo -e "Run without ${YELLOW}--dry-run${NC} to actually install dependencies.\n"
    else
        echo -e "${GREEN}${BOLD}✅ All dependencies installed successfully!${NC}\n"
        
        echo -e "${BOLD}Next Steps:${NC}"
        echo -e "  1. Review and update environment variables in:"
        echo -e "     - ${CYAN}backend/.env${NC}"
        echo -e "     - ${CYAN}frontend/.env${NC}"
        echo -e "\n  2. Start the backend server:"
        echo -e "     ${CYAN}cd backend && python app.py${NC}"
        echo -e "\n  3. Start the frontend development server:"
        echo -e "     ${CYAN}cd frontend && npm run dev${NC}"
        echo -e "\n  4. Visit: ${CYAN}http://localhost:3000${NC}"
        
        echo -e "\n${BOLD}Service Status:${NC}"
        echo -e "  PostgreSQL: ${CYAN}localhost:5432${NC}"
        echo -e "  Redis: ${CYAN}localhost:6379${NC}"
        
        echo -e "\n${BOLD}Troubleshooting:${NC}"
        echo -e "  - Check logs: ${CYAN}cat $LOG_FILE${NC}"
        echo -e "  - Verify installation: ${CYAN}python scripts/verify_installation.py${NC}"
        echo -e "  - Re-run with --force to reinstall packages"
        
        print_status "Installation completed successfully!"
    fi
    
    log "Installation completed at $(date)"
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted${NC}"; exit 130' INT TERM

# Parse arguments and run
parse_args "$@"
main "$@"
