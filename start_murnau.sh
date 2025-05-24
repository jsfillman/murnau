#!/bin/bash

# Murnau Synthesizer Startup Script
# This script starts JACK audio server, compiles and runs the Faust synth, and launches the GUI

set -e  # Exit on any error

echo "🎹 Starting Murnau Synthesizer..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down Murnau...${NC}"
    
    # Kill the synth process if it's running
    if [ ! -z "$SYNTH_PID" ]; then
        echo "Stopping synthesizer..."
        kill $SYNTH_PID 2>/dev/null || true
    fi
    
    # Kill the GUI process if it's running
    if [ ! -z "$GUI_PID" ]; then
        echo "Stopping GUI..."
        kill $GUI_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Murnau shut down cleanly.${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check for required dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command_exists jackd; then
    echo -e "${RED}Error: JACK not found. Please install JACK audio server.${NC}"
    echo "On macOS with Homebrew: brew install jack"
    exit 1
fi

if ! command_exists faust2jackconsole; then
    echo -e "${RED}Error: Faust compiler not found. Please install Faust.${NC}"
    echo "Visit: https://faust.grame.fr"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 not found.${NC}"
    exit 1
fi

# Check if Python dependencies are installed
echo -e "${BLUE}Checking Python dependencies...${NC}"
python3 -c "import PyQt6, mido, pythonosc" 2>/dev/null || {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt || {
        echo -e "${RED}Failed to install Python dependencies. Please run: pip3 install -r requirements.txt${NC}"
        exit 1
    }
}

# Set PYTHONPATH to include current directory for module imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Step 1: Start JACK if not already running
echo -e "${BLUE}Starting JACK audio server...${NC}"

# Check if JACK is already running
if pgrep -x "jackd" > /dev/null; then
    echo -e "${GREEN}JACK is already running.${NC}"
else
    # Start JACK with CoreAudio on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Starting JACK with CoreAudio driver..."
        jackd -d coreaudio -r 44100 -p 256 &
        JACK_PID=$!
        sleep 3  # Give JACK time to start
        
        # Check if JACK started successfully
        if ! pgrep -x "jackd" > /dev/null; then
            echo -e "${RED}Failed to start JACK. Please check your audio setup.${NC}"
            exit 1
        fi
        echo -e "${GREEN}JACK started successfully.${NC}"
    else
        # Linux - try ALSA first, then PulseAudio
        echo "Starting JACK with ALSA driver..."
        jackd -d alsa -r 44100 -p 256 &
        JACK_PID=$!
        sleep 3
        
        if ! pgrep -x "jackd" > /dev/null; then
            echo "ALSA failed, trying PulseAudio bridge..."
            pulseaudio --start
            jack_control start
            sleep 2
        fi
        
        if ! pgrep -x "jackd" > /dev/null; then
            echo -e "${RED}Failed to start JACK. Please check your audio setup.${NC}"
            exit 1
        fi
        echo -e "${GREEN}JACK started successfully.${NC}"
    fi
fi

# Step 2: Compile and start the Faust synthesizer
echo -e "${BLUE}Compiling Faust synthesizer...${NC}"

# The DSP file should be in the root directory for compilation
# (Source code is maintained in src/murnau/dsp/)
if [ ! -f "legato_synth.dsp" ]; then
    echo -e "${RED}Error: legato_synth.dsp not found in current directory.${NC}"
    echo -e "${YELLOW}Note: The DSP source is in src/murnau/dsp/${NC}"
    exit 1
fi

# Create build directory if it doesn't exist
mkdir -p build

# Compile the Faust DSP to build directory
faust2jackconsole -osc legato_synth.dsp -o build/legato_synth || {
    echo -e "${RED}Failed to compile Faust synthesizer.${NC}"
    exit 1
}

echo -e "${GREEN}Synthesizer compiled successfully.${NC}"

# Start the synthesizer
echo -e "${BLUE}Starting synthesizer...${NC}"
./build/legato_synth &
SYNTH_PID=$!

# Wait a moment for the synth to initialize
sleep 2

# Check if synth is still running
if ! kill -0 $SYNTH_PID 2>/dev/null; then
    echo -e "${RED}Synthesizer failed to start or crashed.${NC}"
    exit 1
fi

echo -e "${GREEN}Synthesizer started successfully (PID: $SYNTH_PID).${NC}"

# Step 3: Start the Murnau GUI
echo -e "${BLUE}Starting Murnau GUI...${NC}"

# Check for the entry point script in scripts directory
if [ -f "scripts/run_murnau.py" ]; then
    # Use the robust entry point if available
    python3 scripts/run_murnau.py legato_synth_stereo 5510 &
    GUI_PID=$!
elif [ -f "scripts/murnau_ui.py" ]; then
    # Fall back to the original entry point
    python3 scripts/murnau_ui.py legato_synth_stereo 5510 &
    GUI_PID=$!
else
    echo -e "${RED}Error: No Murnau entry point found.${NC}"
    echo -e "${YELLOW}Looking in scripts/ directory${NC}"
    cleanup
    exit 1
fi

# Wait a moment for the GUI to start
sleep 2

# Check if GUI is still running
if ! kill -0 $GUI_PID 2>/dev/null; then
    echo -e "${RED}GUI failed to start.${NC}"
    cleanup
    exit 1
fi

echo -e "${GREEN}Murnau GUI started successfully (PID: $GUI_PID).${NC}"
echo ""
echo -e "${GREEN}🎹 Murnau Synthesizer is now running!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all processes and exit.${NC}"
echo ""
echo "Components running:"
echo "  • JACK audio server"
echo "  • Faust synthesizer (OSC port 5510)"
echo "  • Murnau GUI"
echo ""

# Wait for user to interrupt or for processes to die
while kill -0 $SYNTH_PID 2>/dev/null && kill -0 $GUI_PID 2>/dev/null; do
    sleep 1
done

# If we get here, one of the processes died
echo -e "${RED}One of the processes has stopped unexpectedly.${NC}"
cleanup