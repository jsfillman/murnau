# Murnau Synthesizer Makefile

.PHONY: all build clean install test run start help

# Default target
all: build

# Build the Faust synthesizer
build:
	@echo "Building Murnau synthesizer..."
	@mkdir -p build
	faust2jackconsole -osc legato_synth.dsp -o build/legato_synth

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ htmlcov/ .coverage

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

# Run tests
test:
	@echo "Running tests..."
	pytest

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term

# Run the UI directly (assumes synth is already running)
run-ui:
	@echo "Starting Murnau UI..."
	python scripts/run_murnau.py

# Start everything (JACK, synth, and UI)
start:
	@echo "Starting Murnau..."
	./start_murnau.sh

# Play test melody
melody:
	python scripts/melody.py

# Run ramp test
ramp:
	python scripts/ramp_test.py

# Help
help:
	@echo "Murnau Synthesizer - Available targets:"
	@echo "  make build         - Build the Faust synthesizer"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make install       - Install Python dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make run-ui        - Start the UI (synth must be running)"
	@echo "  make start         - Start everything (JACK, synth, UI)"
	@echo "  make melody        - Play test melody"
	@echo "  make ramp          - Run frequency ramp test"
	@echo "  make help          - Show this help message"