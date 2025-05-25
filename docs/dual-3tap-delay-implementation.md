# Dual 3-Tap Delay Implementation Document

## Overview

This document outlines the implementation of a dual 3-tap delay effect for the Murnau synthesizer. The feature adds independent 3-tap delays to both left and right channels, enabling complex rhythmic patterns, stereo width enhancement, and ambient textures.

## Feature Specification

### Core Functionality
- **Dual Channel**: Independent delay processing for left and right channels
- **3 Taps per Channel**: Each channel has 3 independently controllable delay taps
- **Feedback Loop**: Configurable feedback for each channel
- **Dry/Wet Mixing**: Adjustable balance between original and delayed signals
- **Real-time Control**: All parameters controllable via OSC

### Signal Flow Integration

#### Current Signal Path
```
Oscillator → Envelope → Filter → Gain → Output
```

#### New Signal Path with Delays
```
Oscillator → Envelope → Filter → 3-Tap Delay → Gain → Output
                                      ↓
                                 Feedback Loop
```

## Technical Specifications

### Parameters (18 Total)

#### Left Channel Parameters (9)
| Parameter | OSC Address | Range | Default | Description |
|-----------|-------------|-------|---------|-------------|
| `delay_L_enable` | `/delay_L_enable` | 0-1 | 0 | Enable/disable left delay |
| `delay_L_tap1_time` | `/delay_L_tap1_time` | 0-2000ms | 125ms | First tap delay time |
| `delay_L_tap1_level` | `/delay_L_tap1_level` | 0-1 | 0.3 | First tap output level |
| `delay_L_tap2_time` | `/delay_L_tap2_time` | 0-2000ms | 250ms | Second tap delay time |
| `delay_L_tap2_level` | `/delay_L_tap2_level` | 0-1 | 0.2 | Second tap output level |
| `delay_L_tap3_time` | `/delay_L_tap3_time` | 0-2000ms | 500ms | Third tap delay time |
| `delay_L_tap3_level` | `/delay_L_tap3_level` | 0-1 | 0.1 | Third tap output level |
| `delay_L_feedback` | `/delay_L_feedback` | 0-0.95 | 0.2 | Feedback amount |
| `delay_L_mix` | `/delay_L_mix` | 0-1 | 0.3 | Dry/wet mix (0=dry, 1=wet) |

#### Right Channel Parameters (9)
Same structure as left channel but with `_R` suffix and slightly different default timing:
- `delay_R_tap1_time`: 150ms (offset for stereo width)
- `delay_R_tap2_time`: 300ms
- `delay_R_tap3_time`: 600ms

### Memory Requirements

#### Delay Line Buffer Size
- **Maximum delay time**: 2000ms
- **Sample rate**: 44,100 Hz (typical)
- **Samples per channel**: 2000ms × 44,100 Hz / 1000 = 88,200 samples
- **Total samples (stereo)**: 176,400 samples
- **Memory usage**: ~688 KB (assuming 4 bytes per sample)

## Implementation Details

### Faust DSP Code Structure

#### 1. Parameter Declarations
```faust
// === Delay Controls (Left Channel) ===
delay_L_enable = checkbox("delay_L_enable[osc:/delay_L_enable]");
delay_L_tap1_time = hslider("delay_L_tap1_time[osc:/delay_L_tap1_time]", 125, 0, 2000, 1);
delay_L_tap1_level = hslider("delay_L_tap1_level[osc:/delay_L_tap1_level]", 0.3, 0, 1, 0.01);
// ... (continue for all 18 parameters)
```

#### 2. Delay Line Implementation
```faust
// Convert milliseconds to samples
ms_to_samples(ms) = ms * ma.SR / 1000;
max_delay_samples = ms_to_samples(2000);

// Left channel delay processing
delay_L_process(input) = 
    delay_line_L, taps_sum_L, output_L
with {
    // Feedback loop
    delay_input_L = input + (taps_sum_L * delay_L_feedback);
    
    // Delay line
    delay_line_L = de.delay(max_delay_samples, delay_input_L);
    
    // Three taps
    tap1_L = delay_line_L(ms_to_samples(delay_L_tap1_time)) * delay_L_tap1_level;
    tap2_L = delay_line_L(ms_to_samples(delay_L_tap2_time)) * delay_L_tap2_level;
    tap3_L = delay_line_L(ms_to_samples(delay_L_tap3_time)) * delay_L_tap3_level;
    
    // Sum taps
    taps_sum_L = tap1_L + tap2_L + tap3_L;
    
    // Dry/wet mix
    output_L = select2(delay_L_enable,
        input,  // Bypass when disabled
        input * (1 - delay_L_mix) + taps_sum_L * delay_L_mix
    );
};
```

#### 3. Integration into Main Process
```faust
// Apply delays after filters, before gain
delayed_sigL = sigL : delay_L_process;
delayed_sigR = sigR : delay_R_process;

// Final output
process = delayed_sigL * gain, delayed_sigR * gain;
```

### Safety Considerations

#### Feedback Stability
- **Maximum feedback**: Limited to 0.95 to prevent runaway feedback
- **Soft limiting**: Consider adding soft limiting to feedback path
- **Zero-delay protection**: Ensure minimum delay time > 0 to prevent infinite loops

#### Parameter Validation
- **Delay time ordering**: No enforcement of tap1 < tap2 < tap3 (allows creative routing)
- **Level limiting**: All levels clamped to 0-1 range
- **Feedback limiting**: Feedback clamped to 0-0.95 range

## Performance Considerations

### CPU Usage
- **Delay lines**: 2 × 88,200 sample circular buffers
- **Interpolation**: Linear interpolation for fractional delay times
- **Tap processing**: 6 delay taps total (3 per channel)
- **Estimated CPU**: ~5-10% additional load on modern systems

### Memory Access Patterns
- **Sequential writes**: Delay line input (cache-friendly)
- **Random reads**: Tap outputs (potential cache misses)
- **Optimization**: Consider SIMD operations for tap processing

## Testing Strategy

### Unit Tests
1. **Bypass functionality**: Verify clean bypass when disabled
2. **Single tap**: Test each tap individually
3. **Feedback stability**: Test feedback at maximum settings
4. **Parameter ranges**: Verify all parameters respect their ranges

### Integration Tests
1. **Signal continuity**: Ensure no clicks/pops when enabling/disabling
2. **Parameter changes**: Smooth transitions when adjusting delay times
3. **Extreme settings**: Test with maximum delay times and feedback

### Musical Tests
1. **Rhythmic patterns**: Test with musical delay times (1/8, 1/4, 1/2 notes)
2. **Stereo width**: Verify stereo imaging with offset L/R timings
3. **Ambient textures**: Test long delays with feedback

## UI Integration

### Parameter Grouping
```
┌─ Delay Left ─────────────────┐  ┌─ Delay Right ────────────────┐
│ Enable: [x]                  │  │ Enable: [x]                  │
│ Tap 1: Time[125] Level[0.3]  │  │ Tap 1: Time[150] Level[0.3]  │
│ Tap 2: Time[250] Level[0.2]  │  │ Tap 2: Time[300] Level[0.2]  │
│ Tap 3: Time[500] Level[0.1]  │  │ Tap 3: Time[600] Level[0.1]  │
│ Feedback: [0.2]              │  │ Feedback: [0.2]              │
│ Mix: [0.3]                   │  │ Mix: [0.3]                   │
└──────────────────────────────┘  └──────────────────────────────┘
```

### Future Enhancements
- **Link L/R**: Button to synchronize left and right parameters
- **Tempo sync**: BPM-based delay times
- **Presets**: Common delay patterns (ping-pong, dotted eighth, etc.)
- **Visualization**: Real-time display of delay taps

## Implementation Phases

### Phase 1: Core Implementation
1. Add parameter declarations to DSP file
2. Implement basic delay line structure
3. Add single tap per channel
4. Test compilation and basic functionality

### Phase 2: Multi-tap Extension
1. Extend to 3 taps per channel
2. Add feedback loops
3. Implement dry/wet mixing
4. Test stability and performance

### Phase 3: Integration & Polish
1. Integrate with existing signal flow
2. Add enable/disable functionality
3. Optimize performance
4. Comprehensive testing

### Phase 4: UI Integration
1. Add delay controls to PyQt6 interface
2. Implement OSC parameter mapping
3. Add visual feedback
4. User testing and refinement

## Risk Assessment

### High Risk
- **Feedback instability**: Could cause audio damage if not properly limited
- **Memory allocation**: Large delay buffers could cause memory issues

### Medium Risk
- **CPU performance**: Additional processing load
- **Parameter complexity**: 18 new parameters increase UI complexity

### Low Risk
- **Signal quality**: Delay implementation is well-understood
- **Integration**: Additive nature minimizes disruption to existing code

## Success Criteria

### Functional Requirements
- [ ] All 18 parameters controllable via OSC
- [ ] Clean bypass when disabled
- [ ] Stable feedback up to 0.95
- [ ] No audio artifacts during parameter changes

### Performance Requirements
- [ ] < 10% additional CPU usage
- [ ] < 1MB additional memory usage
- [ ] Real-time parameter updates without dropouts

### Quality Requirements
- [ ] No audible aliasing or artifacts
- [ ] Smooth parameter transitions
- [ ] Consistent behavior across different sample rates

## Conclusion

The dual 3-tap delay implementation represents a significant enhancement to Murnau's sound design capabilities while maintaining the synthesizer's core architecture. The additive nature of the effect minimizes implementation risk while providing substantial creative potential for users.

The modular design allows for future extensions such as tempo synchronization, additional tap counts, or alternative delay algorithms without major architectural changes. 