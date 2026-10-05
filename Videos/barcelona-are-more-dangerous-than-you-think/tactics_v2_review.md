# Contextual tactical animation revision

33 unique passage-specific MP4 assets replace the 33 existing tactical slots. All 177 other shots and every duration, narration anchor and timeline position remain unchanged.

All clips: 1920×1080, 30 fps, start offset zero, silent, no on-screen text. Each schematic is interpretation, not reconstructed player tracking.

QA: inspected five three-phase contact sheets; validated resolution, frame rate and sufficient duration for all assets. No final master rendered by this task.

## Affected sections

- early_damage: 1 slots
- yamal_dilemma: 4 slots
- raphinha_space: 3 slots
- midfield_choices: 7 slots
- flick_mechanism: 8 slots
- additional_weapons: 2 slots
- levante_warning: 1 slots
- european_test: 1 slots
- opponents_choices: 4 slots
- payoff: 2 slots

## Files

- create_tactics_v2.py: editable scene builder using original create_tactics.py drawing primitives.
- tactics_v2_mapping.json: exact label-to-asset mapping, interpretation, old source and old offset.
- plan_edit.py: contextual mapping applied to tactical slots only.
- long_form_project.json, shot_timeline.json, 04 clip map.csv: tactical asset paths and starts updated.
- _tmp/tactics_v2_qa/contact_01.jpg through contact_05.jpg: setup/midpoint/outcome for every clip.
- _tmp/tactics_v2_qa/validation.json: media and invariant checks.

## Source headroom fix

Each source now includes an additional 1.2-second final-frame tail after its complete original action. Existing action frames are preserved with stream-copy concatenation and checked by decoded-frame MD5. The edit durations, narration timing and rendered final master are unchanged. The generator also retains the original action denominator and adds 36 tail frames for reproducibility. Pixel checks: _tmp/tactics_v2_qa/headroom/pixel_preservation.json.
