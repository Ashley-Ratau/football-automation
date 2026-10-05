## Session 1 — 2026-09-18

**Strategy:** Preserve the approved narration, timing, music, and shot order while correcting the vertical presentation.
**Decisions:** Rebuilt all 16 B-roll assets as full-frame 1080×1920 center crops with no blurred padding. Reduced all 64 FlowLine caption clips from 0.065 to 0.048 frame-height font size; matched the preview caption size at 56 px.
**Reasoning log:** The blurred background was baked into the generated shot media, so replacing the underlying shot files was necessary; a timeline zoom alone would retain the blur.
**Outstanding:** Review framing in FlowLine and adjust individual crop centers if a key player is cut off in any shot.

## Session 2 — 2026-09-18

**Strategy:** Establish a reusable social-caption system instead of continuing with one-off styling.
**Decisions:** Applied the new Social Bold look to all 64 captions, fixed every caption to the exact centre anchor, and rebuilt the preview. Added four caption choices to FlowLine's caption dialog: Social Bold, Highlight, Boxed, and Clean; Centre is now the default placement.
**Reasoning log:** Caption generation previously bypassed FlowLine's preset knowledge and varied only by size and placement. The new template layer owns typography, outline, background, tracking, and shadow while placement remains one shared transform.
**Outstanding:** Package the new FlowLine binary after the Windows native dependency build completes; later add per-word active highlighting and entrance animation for a closer CapCut/TikTok treatment.
