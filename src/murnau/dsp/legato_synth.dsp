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

// === Delay Controls (Left Channel) ===
delay_L_enable = checkbox("delay_L_enable[osc:/delay_L_enable]");
delay_L_tap1_time = hslider("delay_L_tap1_time[osc:/delay_L_tap1_time]", 125, 0, 2000, 1);
delay_L_tap1_level = hslider("delay_L_tap1_level[osc:/delay_L_tap1_level]", 0.3, 0, 1, 0.01);
delay_L_tap2_time = hslider("delay_L_tap2_time[osc:/delay_L_tap2_time]", 250, 0, 2000, 1);
delay_L_tap2_level = hslider("delay_L_tap2_level[osc:/delay_L_tap2_level]", 0.2, 0, 1, 0.01);
delay_L_tap3_time = hslider("delay_L_tap3_time[osc:/delay_L_tap3_time]", 500, 0, 2000, 1);
delay_L_tap3_level = hslider("delay_L_tap3_level[osc:/delay_L_tap3_level]", 0.1, 0, 1, 0.01);
delay_L_feedback = hslider("delay_L_feedback[osc:/delay_L_feedback]", 0.2, 0, 0.95, 0.01);
delay_L_mix = hslider("delay_L_mix[osc:/delay_L_mix]", 0.3, 0, 1, 0.01);

// === Delay Controls (Right Channel) ===
delay_R_enable = checkbox("delay_R_enable[osc:/delay_R_enable]");
delay_R_tap1_time = hslider("delay_R_tap1_time[osc:/delay_R_tap1_time]", 150, 0, 2000, 1);
delay_R_tap1_level = hslider("delay_R_tap1_level[osc:/delay_R_tap1_level]", 0.3, 0, 1, 0.01);
delay_R_tap2_time = hslider("delay_R_tap2_time[osc:/delay_R_tap2_time]", 300, 0, 2000, 1);
delay_R_tap2_level = hslider("delay_R_tap2_level[osc:/delay_R_tap2_level]", 0.2, 0, 1, 0.01);
delay_R_tap3_time = hslider("delay_R_tap3_time[osc:/delay_R_tap3_time]", 600, 0, 2000, 1);
delay_R_tap3_level = hslider("delay_R_tap3_level[osc:/delay_R_tap3_level]", 0.1, 0, 1, 0.01);
delay_R_feedback = hslider("delay_R_feedback[osc:/delay_R_feedback]", 0.2, 0, 0.95, 0.01);
delay_R_mix = hslider("delay_R_mix[osc:/delay_R_mix]", 0.3, 0, 1, 0.01);

// === Delay Implementation ===
// Convert milliseconds to samples
ms_to_samples(ms) = ms * ma.SR / 1000;
max_delay_samples = ms_to_samples(2000);

// Left channel delay processing (basic 3-tap, no feedback for now)
delay_L_process(input) = output_L
with {
    // Three taps using @ operator for delays
    tap1_L = input : @(ms_to_samples(delay_L_tap1_time)) : *(delay_L_tap1_level);
    tap2_L = input : @(ms_to_samples(delay_L_tap2_time)) : *(delay_L_tap2_level);
    tap3_L = input : @(ms_to_samples(delay_L_tap3_time)) : *(delay_L_tap3_level);
    
    // Sum taps
    taps_sum_L = tap1_L + tap2_L + tap3_L;
    
    // Dry/wet mix
    output_L = select2(delay_L_enable,
        input,  // Bypass when disabled
        input * (1 - delay_L_mix) + taps_sum_L * delay_L_mix
    );
};

// Right channel delay processing (basic 3-tap, no feedback for now)
delay_R_process(input) = output_R
with {
    // Three taps using @ operator for delays
    tap1_R = input : @(ms_to_samples(delay_R_tap1_time)) : *(delay_R_tap1_level);
    tap2_R = input : @(ms_to_samples(delay_R_tap2_time)) : *(delay_R_tap2_level);
    tap3_R = input : @(ms_to_samples(delay_R_tap3_time)) : *(delay_R_tap3_level);
    
    // Sum taps
    taps_sum_R = tap1_R + tap2_R + tap3_R;
    
    // Dry/wet mix
    output_R = select2(delay_R_enable,
        input,  // Bypass when disabled
        input * (1 - delay_R_mix) + taps_sum_R * delay_R_mix
    );
};

// Apply delays to filtered signals
delayed_sigL = sigL : delay_L_process;
delayed_sigR = sigR : delay_R_process;

// === Gain Control ===
gain = hslider("gain[osc:/gain]", 1.0, 0, 1, 0.01);

// === Stereo Output ===
process = delayed_sigL * gain, delayed_sigR * gain; 