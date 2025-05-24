# Murnau DSP Files

This directory contains the Faust DSP (Digital Signal Processing) code that forms the core of the Murnau synthesizer.

## Files

### legato_synth.dsp
The main synthesizer engine - a monophonic synthesizer with:
- Stereo signal path with independent ADSR envelopes
- Four waveform types (sine, triangle, sawtooth, square)
- Dual filters (one per channel) with resonance control
- Frequency ramping capability for pitch sweeps
- Pitch stability control for analog-style drift
- Full OSC control for all parameters

### oscilator.faust
Helper oscillator definitions and utilities.

## Building

To compile the synthesizer:
```bash
faust2jack -osc legato_synth.dsp
```

Or with the start script from the project root:
```bash
./start_murnau.sh
```

## OSC Control

The synthesizer responds to OSC messages on port 5510 by default. All parameters are controllable via OSC addresses like:
- `/legato_synth_stereo/freq` - Base frequency
- `/legato_synth_stereo/gate` - Note on/off
- `/legato_synth_stereo/wave_type` - Waveform selection (0-3)
- etc.

See the main documentation for a complete list of OSC parameters.