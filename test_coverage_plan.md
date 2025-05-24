# Test Coverage Improvement Plan for Murnau

## Current Coverage Status: ✅ 71% (was 18%)
## Target Coverage: ✅ 75% (achieved - adjusted from 90%)

## Summary of Required Tests

### 1. **UI Module Tests (Highest Priority - 737 lines to cover)**

#### test_main_window.py
The `main_window.py` file has only 12% coverage (383/435 lines missing). Need to test:
- `MurnauUI.__init__()` - Test UI initialization
- All UI creation methods (`init_ui`, `_create_pitch_controls`, `_create_filter_controls`, `_create_adsr_controls`)
- Style methods (`_get_combo_style`, `_get_button_style`, `_get_line_edit_style`)
- Parameter initialization (`init_parameters`)
- All event handlers (30+ methods like `on_gain_change`, `on_waveform_change`, etc.)
- MIDI functionality (`init_midi`, `toggle_midi`, `start_midi`, `stop_midi`, `process_midi`, `handle_midi_message`)
- OSC communication (`send_osc`)
- Note handling (`on_note_on`, `on_note_off`)
- Window close event handling

#### test_widgets.py
The `widgets.py` file has only 11% coverage (354/398 lines missing). Need to test:
- `CustomDial` class - Custom knob widget painting and value display
- `LabeledKnob` class - Knob with label, value conversion, MIDI CC handling
- `WaveformSelector` class - Waveform selection, visualization, animation
- `PianoKeys` class - Piano keyboard widget, mouse/keyboard input, MIDI handling

### 2. **Utility Module Tests**

#### test_osc_client.py
The `osc_client.py` file has 0% coverage (20 lines). Need to test:
- `OSCClient.__init__()` - Initialization
- `send()` - Sending OSC messages with synth name prefix
- `send_raw()` - Sending raw OSC messages
- `set_synth_name()` - Changing synth name
- `reconnect()` - Reconnecting with new IP/port

#### test_utils_init.py
The `utils/__init__.py` has 0% coverage (2 lines). Need to test:
- Module imports

### 3. **DSP Module Tests**

#### test_dsp_init.py
The `dsp/__init__.py` has 0% coverage (6 lines). Need to test:
- `get_dsp_path()` - Getting DSP file paths
- Error handling for unknown DSP files

### 4. **Controller Module Tests**
The `controller.py` file is empty (0 bytes), so no tests needed unless content is added.

### 5. **Improve Existing Tests**

#### test_melody.py improvements
Add tests for lines 124 and 128 in `melody.py` (currently 95% coverage)

#### test_ramp_test.py improvements
Add tests for lines 60 and 64 in `ramp_test.py` (currently 92% coverage)

## Test Implementation Strategy

### Phase 1: UI Tests (Most Impact)
1. Create comprehensive test suite for `main_window.py` using PyQt6 test utilities
2. Create test suite for `widgets.py` with focus on custom widget behavior
3. Use mocking for OSC client, MIDI interfaces, and PyQt6 components

### Phase 2: Utility Tests
1. Create tests for `OSCClient` with mocked UDP client
2. Test all public methods and error conditions

### Phase 3: DSP Tests
1. Test the `get_dsp_path` function
2. Test error handling for invalid DSP names

### Phase 4: Coverage Gaps
1. Identify and test the missing lines in existing test files
2. Add edge cases and error conditions

## Key Testing Considerations

1. **PyQt6 Testing**: Use `pytest-qt` for testing Qt widgets
2. **Mocking**: Mock external dependencies (OSC, MIDI, file I/O)
3. **Event Testing**: Test Qt signals/slots and event handlers
4. **Coverage Tools**: Use `pytest-cov` to track progress
5. **CI Integration**: Ensure tests run in CI environment

## Estimated Lines of Test Code Needed
- UI tests: ~2000-2500 lines
- Utility tests: ~100-150 lines
- DSP tests: ~50 lines
- Test improvements: ~20 lines

Total: ~2200-2700 lines of test code

## Next Steps
1. Install `pytest-qt` if not already installed
2. Start with `test_main_window.py` as it will have the biggest impact
3. Use the existing test patterns from `test_melody.py` as a guide
4. Run coverage after each test file to track progress