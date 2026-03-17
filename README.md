# Narrative Coupling Demo

## What this demo shows

This is a minimal deterministic companion demo for the paper "Narrative Coupling."
It replays the same fixed event stream across multiple profile settings and shows how
different active fields and coupling parameters produce different thematic
trajectories over time.

The demo focuses on temporal interpretive accumulation inside one profile at a time.
It is meant to be small, inspectable, and easy to replay from the command line.

## What it does not claim

This project does not claim to model full cognition, social interpretation, policy,
or memory in any realistic sense. It does not use machine learning, embeddings, or
probabilistic sampling. It is a transparent toy mechanism for illustrating one
specific point about path-dependent thematic drift.

## Related paper

This demo is a runnable companion to the *Narrative Coupling* paper:

- Paper (Zenodo): https://zenodo.org/records/19041297

If you use or discuss this demo, please read the paper for the full conceptual framing and scope.

## Themes

The demo uses exactly three themes:

- warning
- return
- loss

Each event has deterministic symbolic tags and theme hints. Theme totals accumulate
through time, decay between steps, receive contradiction penalties, and are clamped
by per-theme saturation caps.

## Profiles

The demo includes exactly three profiles:

- `low_coupling_contradiction_sensitive`
- `moderate_balanced`
- `high_coupling_weak_damping`

They differ in coupling gain, decay, contradiction damping, saturation caps,
state-weighting, and modest initial field / initial theme biases.

## Event streams

Two streams are included:

- `neutral`: a six-event ambiguous stream intended to produce visibly different
  thematic trajectories across profiles
- `break`: a shorter contradiction-heavy stream intended to test how quickly
  profiles revise under corrective evidence

## Example final results

Sample deterministic results from the current parameters:

| Stream | Profile | Warning | Return | Loss | Dominant |
| --- | --- | ---: | ---: | ---: | --- |
| neutral | low_coupling_contradiction_sensitive | 0.411 | 0.269 | 0.506 | loss |
| neutral | moderate_balanced | 1.442 | 1.214 | 1.382 | warning |
| neutral | high_coupling_weak_damping | 2.873 | 2.470 | 2.512 | warning |
| break | low_coupling_contradiction_sensitive | 0.079 | 1.635 | 0.158 | return |
| break | moderate_balanced | 0.542 | 2.939 | 0.463 | return |
| break | high_coupling_weak_damping | 1.343 | 3.000 | 0.945 | return |

## Update logic in plain English

For each event, the engine:

1. Reads the event tags and theme hints.
2. Computes overlap for each theme from the event's theme hint plus a transparent
   amplification term derived from the current active field.
3. Converts overlap into theme charge using:
   `coupling_gain * state_weight * overlap`
4. Applies contradiction penalties to any event-declared contradiction targets.
5. Updates theme totals by applying decay, then adding charge, then subtracting
   contradiction, then clamping to the theme's saturation cap.
6. Updates the active field by blending prior field weights, current event tags,
   and a small theme-derived contribution.
7. Derives forward bias from normalized theme totals, including the dominant theme
   and ranked theme ordering.

All formulas are deterministic and directly inspectable in the source.

## Why the break stream matters

The break stream is meant to show revision without magical erasure. Contradiction
does not simply delete prior accumulation. It interacts with coupling gain, decay,
contradiction damping, and the active field built up by earlier events, so cleanup
toward `return` can be partial and history-dependent.

## How to read the neutral divergence

The neutral stream is intentionally mixed. Early signal and reappearance cues can
support `return`, interruption and silence can push toward `warning` or `loss`, and
the final mixed location cue can stabilize different end states depending on how
strongly a profile reinforces, forgets, and revises what came before.

## Determinism and replayability

There is no randomness, no external service, and no hidden persistence. Running the
same stream with the same profile always yields the same trace and the same final
theme totals.

## How to run

From a clean clone:

```bash
git clone <repo-url>
cd narrative-coupling-demo
python -m pip install -e .
narrative-coupling-demo --stream neutral
narrative-coupling-demo --stream break
narrative-coupling-demo --stream all
narrative-coupling-demo --stream all --pretty --json-out outputs/narrative_coupling_trace.json
```

You can also run the module form after editable install:

```bash
python -m narrative_coupling_demo.demo --stream all
```

## Expected behavior

- The neutral stream should yield visibly different thematic trajectories across
  profiles, even though the underlying events are identical.
- The break stream should show stronger revision under strong contradiction damping
  and more persistence under weak damping.

The point is not to declare a correct reading of the stream. The point is to show
how active field and coupling parameters steer interpretive accumulation over time.

## Project limits

This is a companion micro-demo, not a full architecture. It models a single profile
processing a single stream at a time. It does not represent memory consolidation,
cross-profile interaction, world models, uncertainty estimates, or learning across
runs.

## License

This project is licensed under CC-BY-NC-4.0 International.

You may use, study, share, and adapt this work for non-commercial purposes with
attribution. Commercial use requires separate permission.

See the [LICENSE](/Users/stephenaputmanjr/Desktop/narrative-coupling-demo/LICENSE) file for details.

## Feedback

Feedback is appreciated. This version is intentionally minimal, and thoughtful
suggestions or practical observations may help improve later iterations.

## Contact

Stephen A. Putman

GitHub: [putmanmodel](https://github.com/putmanmodel)

Email: [putmanmodel@pm.me](mailto:putmanmodel@pm.me)
