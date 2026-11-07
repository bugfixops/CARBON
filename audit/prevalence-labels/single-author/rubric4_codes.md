# Codes for rubric4_audit_sheet.csv

Fill `r4_gesture` with exactly one code for every row, from the report text
(open the URL for the full report if needed). Leave `note` empty or add a remark.

The question is the rubric's own: does reproducing the bug require one of these
specific gestures, performed on the touch screen or with the device? Count a
gesture only if the report states or clearly implies that it triggers the bug or
is needed to reach the state where the bug shows. The report may describe it in
plain words without naming it.

| Code | Meaning |
|---|---|
| `fling` | a fast swipe that leaves content moving (flinging a list, carousel or page); a normal slow scroll or swipe does NOT count |
| `shake` | physically shaking the device (shake-to-undo, shake-to-silence, shake gesture) |
| `drawing` | drawing or writing with a finger or stylus along a path (strokes on a canvas, whiteboard, signature pad, handwriting, unlock pattern) |
| `edge_swipe` | a swipe starting at the screen edge, including the system back gesture, predictive back, or gesture navigation (swipe up from the bottom edge to go home) |
| `one_finger_zoom` | double-tap and then drag up or down without lifting, to zoom |
| `two_finger_rotate` | two fingers turning around each other to rotate a map, image or view |
| `none` | none of these is needed. Taps, typing, ordinary scrolls or swipes, pinches, drags, long presses and device rotation are labelled by the other rubrics and count as `none` here |
