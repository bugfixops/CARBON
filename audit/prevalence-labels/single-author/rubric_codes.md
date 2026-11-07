# Codes for audit_sheet.csv

Fill one code per column for every row, from the report text (open the URL for
the full report). Use exactly these codes. Leave `note` empty or add a remark.

## r1_trigger: what must the reporter do to TRIGGER the bug?
Label a gesture only if the report states or clearly implies that it is needed
to trigger the bug. A gesture that is merely mentioned does not count.

| Code | Meaning |
|---|---|
| `pinch_zoom` | two-finger pinch to zoom in or out |
| `drag_and_drop` | press an item or handle and drag it to a new position (reorder a list, move or resize a widget) |
| `swipe_region` | a swipe or drag that must start or end at a specific place or control: seek bar, slider, screen edge, part of a video, map region |
| `quick_tap` | taps whose timing matters: rapid repeated taps, during an animation or transition, before a timeout |
| `picker_scroll` | turning a number, date or time picker wheel to a value |
| `multi_touch` | any other multi-finger gesture (two-finger swipe or pan, rotation, three fingers) |
| `scroll` | scrolling |
| `swipe` | a directional swipe anywhere |
| `long_press` | long press |
| `double_tap` | double tap |
| `orientation` | rotating the device |
| `none` | taps, typing and navigation (including back) are enough, or the report is not about a GUI interaction |
| `unclear` | the report does not say enough to decide |

## r2_scope: can the bug be reproduced through an app's GUI?

| Code | Meaning |
|---|---|
| `gui` | yes: launching, tapping, typing, gestures, navigation or rotation can trigger it, including crashes on launch, visual glitches, and bugs that need particular data, settings, accounts, hardware or network |
| `not_gui` | no: build, Gradle or dependency errors; a library or SDK bug that only code can trigger; server, CI or release problems; documentation or translation text; a feature request or question |
| `unclear` | the report does not say enough to decide |

When in doubt between `gui` and `not_gui`, choose `gui`.

## r3_any_step: which gesture does ANY step of the reproduction need, including setup?
Be inclusive: count a gesture even if the report only describes it in plain
words ("move the slider", "reorder the items", "resize the widget", "before it
finishes loading"). When in doubt between a gesture and `none`, choose the
gesture. If several gestures could be involved, give the most complex one
(the first group of the r1 table is the complex one).

Codes: the same as r1 without `unclear`: `pinch_zoom`, `drag_and_drop`,
`swipe_region`, `quick_tap`, `picker_scroll`, `multi_touch`, `scroll`, `swipe`,
`long_press`, `double_tap`, `orientation`, `none`.
