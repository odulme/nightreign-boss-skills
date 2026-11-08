#!/usr/bin/env python3
# Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
"""Offline heading model for one attack clip: how far does the boss turn before / during its hits?

Run it before and after every change to TAE 224 (Set Turn Speed) rows or JT7 (Disable Turning) windows. It reproduces the
engine's AI tracking in a simple way: every 1/60 s the boss turns toward the target at the 224 rate of that moment
(0 inside a JT7 window, the NpcParam default rate where no 224 row is active), plus the clip's own root yaw.

  python heading_model.py clip.json
  python heading_model.py --example > clip.json      # writes an example input

Input JSON (times in seconds, angles in degrees, positive = to the right):
  {
    "name": "3006",
    "duration": 12.0,
    "default_rate": 5.0,                  # NpcParam turn rate used where no 224 row is active
    "rates": [[0.0, 12.0, 0.0], [2.13, 3.07, 48.0]],   # 224 rows: start, end, deg/s (later rows win)
    "jt7": [[0.0, 2.13], [3.07, 12.0]],   # Disable Turning windows (force 0)
    "root_yaw": [[0.0, 0.0], [12.0, 0.0]],# optional cumulative clip root yaw samples (t, deg), linear in between
    "hits": [2.5, 4.1],                   # first frame of each damaging event
    "arm": 13.8,                          # distance pivot -> mouth / weapon in m (sideways speed)
    "targets_deg": [30, 60, 90, 150],     # static targets at these bearings
    "strafe": {"distance": 12.0, "speed": 6.0}   # optional: a player strafing sideways from straight ahead
  }

Output per target: engine rotation before the first hit, max turn speed, max mouth sideways speed, heading error at every hit.
Limits: no acceleration model, no Rotate requests (EMEVD), no AI pre-turn; compare variants, do not trust absolutes.
"""
import json
import math
import sys

EXAMPLE = {
    "name": "example",
    "duration": 6.0,
    "default_rate": 5.0,
    "rates": [[0.0, 6.0, 0.0], [0.5, 1.2, 90.0]],
    "jt7": [[0.0, 0.5], [1.2, 6.0]],
    "root_yaw": [[0.0, 0.0], [6.0, 0.0]],
    "hits": [1.6, 2.4],
    "arm": 13.8,
    "targets_deg": [30, 60, 90, 150],
    "strafe": {"distance": 12.0, "speed": 6.0},
}


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def inside(t, spans):
    return any(s <= t < e for s, e in spans)


def rate_at(t, clip):
    if inside(t, [(s, e) for s, e in clip.get("jt7", [])]):
        return 0.0
    r = None
    for s, e, v in clip.get("rates", []):
        if s <= t < e:
            r = v                     # later rows win
    return clip.get("default_rate", 5.0) if r is None else r


def root_yaw_at(t, samples):
    if not samples:
        return 0.0
    if t <= samples[0][0]:
        return samples[0][1]
    for (t0, y0), (t1, y1) in zip(samples, samples[1:]):
        if t0 <= t <= t1:
            return y0 if t1 == t0 else y0 + (y1 - y0) * (t - t0) / (t1 - t0)
    return samples[-1][1]


def simulate(clip, bearing_fn, label):
    dt = 1.0 / 60.0
    dur = clip["duration"]
    hits = sorted(clip.get("hits", []))
    arm = clip.get("arm", 5.0)
    samples = sorted(clip.get("root_yaw", []))
    h = 0.0
    engine_turn_before_hit = 0.0
    max_rate = 0.0
    max_side = 0.0
    errors = []
    hit_i = 0
    t = 0.0
    prev_root = root_yaw_at(0.0, samples)
    first_hit = hits[0] if hits else dur
    while t < dur - 1e-9:
        b = bearing_fn(t)
        r = rate_at(t, clip)
        want = wrap(b - h)
        step = max(-r * dt, min(r * dt, want))
        root = root_yaw_at(t + dt, samples)
        d_root = root - prev_root
        prev_root = root
        if t < first_hit:
            engine_turn_before_hit += abs(step)
        total = step + d_root
        max_rate = max(max_rate, abs(total) / dt)
        max_side = max(max_side, abs(total) / dt * math.pi / 180.0 * arm)
        h += total
        t += dt
        while hit_i < len(hits) and t >= hits[hit_i]:
            errors.append(wrap(bearing_fn(t) - h))
            hit_i += 1
    err = " ".join(f"{e:+6.1f}" for e in errors) or "-"
    print(f"  {label:<14} turn before 1st hit {engine_turn_before_hit:6.1f} deg | max {max_rate:6.1f} deg/s | "
          f"mouth sideways max {max_side:5.1f} m/s | error at hits {err}")


def main(argv):
    if argv and argv[0] == "--example":
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if not argv:
        print(__doc__)
        return 2
    clip = json.load(open(argv[0], encoding="utf-8"))
    print(f"clip {clip.get('name', '?')}  duration {clip['duration']} s  default rate {clip.get('default_rate', 5.0)} deg/s")
    for a in clip.get("targets_deg", [30, 60, 90, 150]):
        simulate(clip, lambda t, a=a: float(a), f"target {a:+.0f}")
    s = clip.get("strafe")
    if s:
        d, v = float(s["distance"]), float(s["speed"])
        simulate(clip, lambda t: math.degrees(math.atan2(v * t, d)), f"strafe {v:g} m/s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
