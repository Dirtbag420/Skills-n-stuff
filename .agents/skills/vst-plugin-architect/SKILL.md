---
name: vst-plugin-architect
description: "Use to design, implement, test, and release audio plugins, especially JUCE, CMake, VST3, CLAP, AU, MIDI effects, real-time DSP, interfaces, and presets."
---

# vst-plugin-architect

## Scope and execution
1. Inspect repository, framework versions, platform, compiler, format targets, licenses, SDK versions, and intended DAW hosts before coding.
2. Separate DSP/audio callback, parameter state, user interface, MIDI handling, serialization, and host wrapper; preserve stable parameter IDs.
3. Keep audio threads real-time safe: no allocation, blocking locks, network, disk IO, dynamic logging, or unbounded computation in processing callbacks.
4. Implement sample-rate and buffer-size changes, parameter smoothing, bypass, reset, denormals, silence, automation, latency and tails.
5. Start with a minimal working DSP processor and tests, then build GUI, presets, oversampling and optional features without hiding incomplete code.
6. Use deterministic DSP tests, impulse and golden-vector checks, offline renders, build matrix, pluginval, and DAW host validation when available.
7. Never report a working VST3 binary or compatibility without an actual compile and host test.

## Skill coordination
Use other installed specialists only if actually available. Do not rely on undocumented device capabilities or claim tools/tests succeeded without running them. Preserve user projects and copyrighted material.

## Output
Give an actionable deliverable, explicit assumptions, sources for externally verified facts, and QA statuses of PASS, FAIL, NOT RUN, or MANUAL REVIEW REQUIRED.

## Provenance
This is a repository-safe, self-contained activation manifest. The previously generated full suite has additional reference files, scripts, data and tests not embedded in this manifest.
