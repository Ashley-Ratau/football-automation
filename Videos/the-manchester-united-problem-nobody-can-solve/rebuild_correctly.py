import json
from pathlib import Path

P = Path(__file__).resolve().parent
cfg_path = P / 'long_form_project.json'
cfg = json.loads(cfg_path.read_text(encoding='utf-8-sig'))

expansions = {
    'cold_open': " The important distinction is between a team that looks better because its roles are clearer and a team that has built answers for every opponent. Those are not the same thing. A short run can hide the difference because confidence turns loose balls into attacks and a compact block makes every decision feel obvious. The harder test arrives when the opponent refuses to give United those moments. That is the test this video is about.",
    'rescue_real': " The rescue also tells us what Carrick is good at. He reduced the number of decisions players had to make, gave the midfield a reliable first pass, and brought the forwards into the game earlier. That matters because confidence in football is often a consequence of structure rather than a mysterious mood. But the same simplification can become predictable when the opponent sits behind the ball. The rescue was real; it was simply narrower than the mythology around it.",
    'where_breaks': " This is why the problem cannot be reduced to one player missing or one midfielder having a bad afternoon. The spacing changes from phase to phase. In possession, United need enough width to move the block, enough occupation between the lines to pin the centre-backs, and enough protection behind the ball to survive the first clearance. When one of those disappears, the other two become liabilities. The team looks organised until the next action asks it to reorganise.",
    'warning_week': " The sequence is useful because it removes the comfort of a single explanation. If every defeat were a transition problem, the answer would be obvious. If every draw were a fitness problem, recruitment would solve it. Instead, United keep reaching the same uncomfortable point: the team can execute a plan when the match follows its preferred script, but the response to disruption is still individual rather than collective. That is where a promising project starts to look unfinished.",
    'tactical_dilemma': " The answer is not to ban risk. Great teams create risk by pushing numbers forward; they just decide in advance which spaces must remain protected. United's best passages have a clear first defender after the turnover, a midfielder screening the central lane, and a winger close enough to counter-press. Their worst passages have none of those relationships. The diagram changes, but the principle should not. Shape is the surface. Spacing and timing are the actual system.",
    'club_cannot_hide': " Recruitment is where the tactical argument becomes an institutional one. A club does not need every player to fit one manager's favourite formation, but it does need a repeatable idea about distances, pressing, progression and defensive cover. Otherwise each transfer window solves the last coach's problem and creates the next coach's problem. Carrick can improve the team, but he cannot personally reconcile years of contradictory squad-building. That responsibility belongs to the football structure around him.",
    'conclusion': " The next phase therefore needs a different kind of patience. It is not patience with poor performances for their own sake; it is patience with a clearly defined model while demanding evidence that the model is becoming more resilient. United should be able to explain what they want the full-backs, pivots, wingers and first defender to do in every game state. If they can, Carrick has a platform. If they cannot, the next reset will only rename the same problem."
}

for section in cfg['sections']:
    if section.get('type') == 'vo' and section.get('name') in expansions:
        marker = expansions[section['name']]
        if marker.strip() not in section['text']:
            section['text'] = section['text'].rstrip() + marker

# The longer Liam narration needs explicit visual coverage. Add distinct
# tactical beats rather than allowing the compositor to loop or freeze shots.
tactical_pool = [
    'assets/broll/tactics_compact_442.mp4',
    'assets/broll/tactics_transition_release.mp4',
    'assets/broll/tactics_low_block_problem.mp4',
    'assets/broll/tactics_right_overload.mp4',
    'assets/broll/tactics_rest_defence_gap.mp4',
    'assets/broll/tactics_game_state_balance.mp4',
]
for section in cfg['sections']:
    if section.get('type') == 'vo':
        existing = {item.get('file') for item in section.get('broll', [])}
        for path in tactical_pool:
            if path not in existing:
                section.setdefault('broll', []).append({
                    'file': path, 'start': 0, 'duration': 4.2,
                    'label': section['name'] + '_tactical_' + Path(path).stem,
                })
        if not any(item.get('label') == section['name'] + '_coverage_extension' for item in section.get('broll', [])):
            section.setdefault('broll', []).append({
                'file': 'assets/broll/tactics_game_state_balance.mp4', 'start': 0,
                'duration': 4.2, 'label': section['name'] + '_coverage_extension'
            })

cfg['settings']['voice_speed'] = 1.0
cfg['settings']['voice_gain_db'] = 0.0
cfg['settings']['min_duration_seconds'] = 480
cfg['settings']['max_duration_seconds'] = 600
cfg['settings']['broll_clip_max_seconds'] = 5.5
cfg['output_filename'] = 'why-every-manchester-united-rebuild-fails-rebuilt.mp4'
cfg['captions']['enabled'] = False
cfg_path.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
print('updated', cfg_path)
