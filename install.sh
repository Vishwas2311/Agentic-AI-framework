#!/usr/bin/env bash
# Genesis E2E Installer for Mac/Linux
# Usage: curl -sSL https://raw.githubusercontent.com/Vishwas2311/Agentic-AI-framework/main/install.sh | bash

set -e

echo ""
echo "========================================"
echo "   Genesis Pro - E2E Installer"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 not found. Install Python 3.11+ from https://python.org"
    exit 1
fi
echo "OK  Python found"

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "WARN Node.js not found. Install from https://nodejs.org for full features."
else
    echo "OK  Node.js found"
fi

# Check Claude Code
if ! command -v claude &>/dev/null; then
    echo "WARN Claude Code CLI not found. Install from https://claude.ai/code for full features."
else
    echo "OK  Claude Code found"
fi

echo ""
echo "Installing genesis-pro from PyPI..."
pip3 install --upgrade genesis-pro
echo "OK  genesis-pro installed"

echo ""
echo "Running Genesis E2E setup..."
genesis install

echo ""
echo "========================================"
echo "   Genesis is ready!"
echo "========================================"
echo ""
echo "Run: genesis launch   -> opens dashboard"
echo "Run: genesis --help   -> see all commands"
echo ""
