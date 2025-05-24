# Murnau: Design Document

## Overview
**Murnau** is a distributed, cinematic synthesizer system designed for expressive, immersive sound synthesis. Drawing inspiration from German Expressionism and built for both live performance and studio exploration, Murnau emphasizes emotion, spatial audio, and modular orchestration.

The architecture separates the expressive UI and input mapping (Python) from the DSP-heavy synth engines (Faust/Jack), enabling low-latency performance and extreme scalability across local and cloud-based compute clusters.

---

## Architecture Summary

### Components:

#### 1. **Frontend: PyQt6 Controller (Python)**
- **UI**: Stylized GUI inspired by silent film title cards.
  - Controls are context-sensitive, tactile, and minimal.
  - Designed for touch or expressive mouse/keyboard control.
- **Input Handling**:
  - MIDI w/ Polyphonic Aftertouch
  - Audio analysis (pitch + amplitude follower)
  - User macros and expression curves
  - **Selectable MIDI input port** via dropdown or auto-detection
- **OSC Routing**:
  - Maps inputs to OSC messages targeting Faust synths
- **Synth Loader**:
  - Frontend dynamically selects and launches **fully compiled Faust synth binaries**
  - Maintains a registry or path map to launchable Faust apps
  - Allows one-click synth switching and relaunch

#### 2. **Backend: Faust Synth Engines (Jack-based)**
- **Synth Units**: Each Faust app represents an oscillator or voice.
  - Receives OSC parameters (freq, amp, mod index, etc.)
  - Outputs audio via Jack
- **Configurable Patches**:
  - Defined in Faust code
  - Dynamically loaded or toggled by controller
- **Routing**:
  - Jack connects Faust outputs to system playback or JACK server (for netjack/distributed routing)

#### 3. **Cluster Orchestration (Future Stage)**
- Each **oscillator runs in a container/pod** (K8s or Nomad)
- Controller deploys pods on-demand
  - Uses job scheduler or orchestration API
- Audio streams back to central JACK server or controller node

---

## Key Features

- **Emotion-Driven Mapping**:
  - Controls mapped to intuitive expressions, not just values (e.g., "pressure" becomes modulation depth)
- **Spatial Audio (7.1.4, Atmos, Ambisonic-ready)**
  - Each oscillator can be panned/staged independently
- **Dynamic Scaling**:
  - Deploy 1–N oscillators depending on system load and musical intent
- **Patch Agnostic**:
  - Frontend supports patch switching without relaunching the system

---

## Development Milestones

### Phase 1: Local Prototype
- [ ] PyQt6 GUI skeleton
- [ ] MIDI-to-OSC and Audio-to-OSC conversion
- [ ] Basic Faust synth app with Jack output
- [ ] UI element mapping (sliders, XY pads, envelopes)
- [ ] MIDI input selector
- [ ] Faust synth launcher integration

### Phase 2: Pod-Based Synthesis
- [ ] Containerize Faust synths
- [ ] OSC discovery and routing to individual pods
- [ ] NetJack integration or RTP routing

### Phase 3: Cluster Expansion
- [ ] Helm chart for deployable synth pods
- [ ] OSC/Audio performance tuning
- [ ] Pod autoscaler based on musical intent or available CPU

---

## UI Concepts
- Film-grain texture background
- Monochrome color palette
- Letterbox layout w/ tabbed control sections
- Mod matrix inspired by silent film intertitles

---

## Future Ideas
- Vector-based UI control mapping (draw your modulation curves)
- External OSC-compatible apps (TouchOSC, Lemur, iPad UI)
- AI-enhanced input modulation (expression modeling)
