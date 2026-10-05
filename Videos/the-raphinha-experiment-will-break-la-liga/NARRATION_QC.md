# Narration QC — revised introductions

Current raw narration total: **323.918367 seconds (5:23.92)**. PASS: within requested 300–360 seconds.

This replaces the earlier 308.500-second measurement. Includes regenerated hook, dilemma and league with spoken pundit introductions. Interview inserts/transitions are additional. Audio was not modified.

| Section | Duration seconds | Text/hash | Peak dBFS | RMS dBFS | Clipped samples |
|---|---:|---|---:|---:|---:|
| hook | 32.972336 | PASS | -7.75 | -29.25 | 0 |
| role | 54.334694 | PASS | -13.8 | -36.23 | 0 |
| dilemma | 58.978685 | PASS | -5.12 | -26.79 | 0 |
| sevilla | 64.737234 | PASS | -7.26 | -29.55 | 0 |
| league | 62.043719 | PASS | -3.98 | -27.1 | 0 |
| limits_payoff | 50.851701 | PASS | -11.43 | -34.63 | 0 |

Alignment/signal result: PASS. All current text and saved hashes match; timestamps are monotonic and within the WAV bounds. No full-scale clipping detected.

Longest detected silence at -40 dBFS with minimum 0.7 seconds: 0.980 seconds.

Keep per-section loudness normalization during assembly: raw RMS levels differ. The initial checks were alignment and signal QC; independent speech recognition is documented below. Detailed metrics are in narration_qc_metrics.json.

## Independent speech recognition

Completed all six current WAVs using cached faster-whisper **small.en**, CPU int8, beam size 5, English, local-files-only; no model download and no audio changes. Full segment timestamps, transcripts and token differences are saved in narration_asr_qc.json.

**Result: no content omissions, repeated phrases, changed numbers or added words detected.** All spoken pundit introductions are present. Differences are US/UK spellings, number formatting and phonetic names:

- Raphinha → Rafina/Raffina; Christensen → Kristensen; Yamal → Jamal.
- Hislop → Hislup; Herculez → Hercules.
- centre/center, defence/defense, recognise/recognize and written/spelled-out numbers.

These name spellings are plausible ASR renderings and do not independently prove mispronunciation. No missing name or unintelligible clause was detected, but human listening remains the stronger check for exact name pronunciation. ASR transcription preserved the narration's wording and meaning throughout all six sections.
