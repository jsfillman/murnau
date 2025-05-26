declare name "legato_synth_stereo";
declare description "Monophonic synth with stereo ADSR + filters";
declare version "1.1";

import("stdfaust.lib");

// === Gate ===
gate = button("gate[osc:/gate]");

// === Base Frequency & Tuning ===
base_freq     = hslider("freq[osc:/freq]", 440, 20, 8000, 0.01);
coarse_tune   = hslider("coarse_tune[osc:/coarse_tune]", 0, -24, 24, 1) : int;
fine_tune     = hslider("fine_tune[osc:/fine_tune]", 0, -100, 100, 1);
stability     = hslider("stability[osc:/stability]", 0, 0, 20, 0.1);

// === Frequency Ramping ===
start_freq_offset = hslider("start_freq_offset[osc:/start_freq_offset]", 0, -200, 200, 1);
end_freq_offset = hslider("end_freq_offset[osc:/end_freq_offset]", 0, -200, 200, 1);
ramp_time = hslider("ramp_time[osc:/ramp_time]", 0, 0, 10, 0.01);

// Simple ramping using integrator
// When gate is on, accumulate time; when gate triggers, reset to 0
gate_trigger = gate : ba.impulsify;
time_step = 1.0 / ma.SR;  // Time per sample

// Accumulate time while gate is on, reset on gate trigger
elapsed_time = (gate * time_step) : (+ : *(1 - gate_trigger)) ~ _;

// Convert to progress (0 to 1) over ramp_time
ramp_progress = min(1.0, elapsed_time / max(0.001, ramp_time));

// Interpolate between start and end offsets
freq_offset_ramp = start_freq_offset + (end_freq_offset - start_freq_offset) * ramp_progress;

// === Pitch Instability ===
random_stability  = gate : ba.sAndH(no.noise * 2 - 1) * stability;
cents_offset      = fine_tune + random_stability;
semitones_offset  = coarse_tune + (cents_offset * 0.01);

// Final frequency calculation - always apply freq_offset_ramp
freq = base_freq + freq_offset_ramp;
freq_with_tuning = freq * pow(2, semitones_offset / 12);

// === Envelope Controls (Dual) ===
attack_L   = hslider("attack_L[osc:/attack_L]", 0.005, 0.001, 5, 0.001);
decay_L    = hslider("decay_L[osc:/decay_L]", 0.1, 0.001, 3, 0.001);
sustain_L  = hslider("sustain_L[osc:/sustain_L]", 0.9, 0, 1, 0.01);
release_L  = hslider("release_L[osc:/release_L]", 0.5, 0.1, 5, 0.01);

attack_R   = hslider("attack_R[osc:/attack_R]", 0.005, 0.001, 5, 0.001);
decay_R    = hslider("decay_R[osc:/decay_R]", 0.1, 0.001, 3, 0.001);
sustain_R  = hslider("sustain_R[osc:/sustain_R]", 0.9, 0, 1, 0.01);
release_R  = hslider("release_R[osc:/release_R]", 0.5, 0.1, 5, 0.01);

// === ADSRs (Dual) ===
env_L = en.adsr(attack_L, decay_L, sustain_L, release_L, gate);
env_R = en.adsr(attack_R, decay_R, sustain_R, release_R, gate);

// === Oscillator ===
wave_type = nentry("wave_type[osc:/wave_type]", 2, 0, 3, 1) : int;

osc_mono = 
    (wave_type == 0) * os.osc(freq_with_tuning) +
    (wave_type == 1) * os.triangle(freq_with_tuning) +
    (wave_type == 2) * os.sawtooth(freq_with_tuning) +
    (wave_type == 3) * os.square(freq_with_tuning);

// === Duplicate oscillator for stereo path ===
osc_L = osc_mono * env_L;
osc_R = osc_mono * env_R;

// === Filter Controls (Dual) ===
cutoffL = hslider("cutoff_L[osc:/cutoff_L]", 2000, 20, 20000, 1);
resL    = hslider("resonance_L[osc:/resonance_L]", 0.5, 0.1, 4, 0.01);

cutoffR = hslider("cutoff_R[osc:/cutoff_R]", 2000, 20, 20000, 1);
resR    = hslider("resonance_R[osc:/resonance_R]", 0.5, 0.1, 4, 0.01);

// === Apply Filter (Dual) ===
sigL = osc_L : fi.resonlp(cutoffL, resL, 1.0) : fi.resonlp(cutoffL, resL, 1.0);
sigR = osc_R : fi.resonlp(cutoffR, resR, 1.0) : fi.resonlp(cutoffR, resR, 1.0);

// === Gain Control ===
gain = hslider("gain[osc:/gain]", 1.0, 0, 1, 0.01);

// === Stereo Output ===
process = sigL * gain, sigR * gain; 