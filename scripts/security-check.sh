#!/bin/bash
set -e

# Security Check Script for llm-benchmarking-py
# This script runs various security checks on the codebase

echo "🔒 Security Check Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}✗${NC} $message"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    else
        echo "  $message"
    fi
}

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    print_status "error" "Poetry is not installed. Please install it first."
    exit 1
fi

print_status "success" "Poetry found"
echo ""

# Check if .env file exists and is not tracked
echo "1️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    print_status "success" ".env file exists"
    
    # Check if .env is in .gitignore
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        print_status "success" ".env is in .gitignore"
    else
        print_status "error" ".env is NOT in .gitignore - THIS IS A SECURITY RISK!"
        exit 1
    fi
else
    print_status "warning" ".env file not found (copy from .env.example if needed)"
fi
echo ""

# Check for potential secrets in code
echo "2️⃣  Scanning for potential secrets in code..."
SECRET_PATTERNS=(
    "api[_-]?key.*=.*['\"][a-zA-Z0-9]{20,}['\"]"
    "password.*=.*['\"][^'\"]{8,}['\"]"
    "secret.*=.*['\"][a-zA-Z0-9]{20,}['\"]"
    "token.*=.*['\"][a-zA-Z0-9]{20,}['\"]"
    "sk-[a-zA-Z0-9]{20,}"
)

secrets_found=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i -E "$pattern" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . 2>/dev/null | grep -v ".env.example" | grep -q .; then
        print_status "error" "Potential secret found matching pattern: $pattern"
        secrets_found=$((secrets_found + 1))
    fi
done

if [ $secrets_found -eq 0 ]; then
    print_status "success" "No obvious secrets found in code"
else
    print_status "error" "Found $secrets_found potential secret(s) - please review and remove them"
fi
echo ""

# Check if safety is installed
echo "3️⃣  Checking for vulnerable dependencies..."
if poetry run safety --version &> /dev/null; then
    print_status "success" "Safety is installed"
    
    # Run safety check
    if poetry run safety check 2>&1 | tee safety_output.tmp; then
        print_status "success" "No known vulnerabilities found in dependencies"
    else
        print_status "error" "Vulnerabilities found in dependencies - please update"
    fi
    rm -f safety_output.tmp
else
    print_status "warning" "Safety not installed. Install with: poetry add --group dev safety"
fi
echo ""

# Check if bandit is installed
echo "4️⃣  Running security linter (Bandit)..."
if poetry run bandit --version &> /dev/null; then
    print_status "success" "Bandit is installed"
    
    # Run bandit
    if poetry run bandit -r . -ll -f txt --exclude ./.venv,./venv 2>&1 | tee bandit_output.tmp; then
        print_status "success" "No high/medium severity issues found"
    else
        print_status "warning" "Potential security issues found - please review"
    fi
    rm -f bandit_output.tmp
else
    print_status "warning" "Bandit not installed. Install with: poetry add --group dev bandit"
fi
echo ""

# Check for subprocess usage with shell=True
echo "5️⃣  Checking for unsafe subprocess usage..."
if grep -r "shell=True" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . 2>/dev/null; then
    print_status "error" "Found subprocess calls with shell=True - potential command injection risk"
else
    print_status "success" "No unsafe subprocess usage found (shell=True)"
fi
echo ""

# Check for debug mode in production files
echo "6️⃣  Checking for debug mode settings..."
if grep -r "debug=True" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . 2>/dev/null; then
    print_status "warning" "Found debug=True in code - ensure it's disabled in production"
else
    print_status "success" "No hardcoded debug=True found"
fi
echo ""

# Summary
echo "================================"
echo "🔍 Security Check Summary"
echo "================================"
echo ""
echo "Review the output above for any issues."
echo ""
echo "📋 Recommended next steps:"
echo "  1. Fix any errors (marked with ✗)"
echo "  2. Review warnings (marked with ⚠)"
echo "  3. Update dependencies: poetry update"
echo "  4. Review SECURITY_RECOMMENDATIONS.md for detailed guidance"
echo ""
echo "For more information:"
echo "  - See SECURITY.md for security policy"
echo "  - See SECURITY_RECOMMENDATIONS.md for detailed recommendations"
echo "  - See SECURITY_CHECKLIST.md for implementation checklist"
echo ""
