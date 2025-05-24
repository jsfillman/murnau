# Murnau Documentation

Welcome to the Murnau synthesizer control interface documentation.

## Contents

- [Design Documentation](design/MurnauDesign.md) - Original design specifications
- [User Guide](user-guide.md) - How to use Murnau
- [Developer Guide](developer-guide.md) - Information for developers
- [API Reference](api-reference.md) - API documentation

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the UI:
   ```bash
   python murnau_ui.py
   ```

3. Play a melody:
   ```bash
   python melody.py
   ```

4. Test frequency ramps:
   ```bash
   python ramp_test.py
   ```

## Architecture

Murnau follows a modular architecture:

- `src/murnau/ui/` - User interface components
- `src/murnau/synth/` - Synthesizer control modules
- `src/murnau/utils/` - Utility modules
- `src/lib/` - External library interfaces

## Testing

Run tests with:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=src --cov-report=html
```