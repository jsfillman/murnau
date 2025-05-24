#!/bin/bash

# Test script to verify the startup sequence works correctly

echo "Testing Murnau startup sequence..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test 1: Check if JACK is available
echo -n "Checking JACK availability... "
if command -v jackd >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} - JACK not found"
    exit 1
fi

# Test 2: Check if Faust is available
echo -n "Checking Faust compiler... "
if command -v faust2jackconsole >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} - Faust compiler not found"
    exit 1
fi

# Test 3: Check if DSP file exists
echo -n "Checking DSP file... "
if [ -f "legato_synth.dsp" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} - legato_synth.dsp not found"
    exit 1
fi

# Test 4: Check Python dependencies
echo -n "Checking Python dependencies... "
if python3 -c "import PyQt6, mido, pythonosc" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} - Missing Python dependencies"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi

# Test 5: Check UI script
echo -n "Checking UI script... "
if [ -f "scripts/run_murnau.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} - UI script not found"
    exit 1
fi

echo ""
echo -e "${GREEN}All checks passed!${NC}"
echo "You can now run: ./start_murnau.sh"