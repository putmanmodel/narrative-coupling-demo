from __future__ import annotations

import json
from pathlib import Path

from .models import Event, Profile, RunTrace, StepTrace, THEMES


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
THEME_TO_FIELD_TAGS: dict[str, dict[str, float]] = {
    "warning": {"signal": 0.35, "distance": 0.2, "gap": 0.25, "conflict": 0.2},
    "return": {"return": 0.45, "confirmation": 0.25, "continuity": 0.2, "reappearance": 0.1},
    "loss": {"silence": 0.35, "gap": 0.25, "distance": 0.25, "break": 0.15},
}


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _round_map(values: dict[str, float], digits: int = 4) -> dict[str, float]:
    return {key: round(val, digits) for key, val in values.items()}


def load_events(path: str | Path) -> list[Event]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [Event(**item) for item in payload]


def load_profiles(path: str | Path) -> list[Profile]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [Profile(**item) for item in payload]


def overlap(event: Event, active_field: dict[str, float]) -> dict[str, float]:
    overlaps: dict[str, float] = {}
    for theme in THEMES:
        hint = event.theme_hints.get(theme, 0.0)
        field_map = THEME_TO_FIELD_TAGS[theme]
        field_alignment = sum(
            active_field.get(tag, 0.0) * weight * event.tags.get(tag, 0.0)
            for tag, weight in field_map.items()
        )
        overlaps[theme] = round(hint + 0.6 * field_alignment, 4)
    return overlaps


def contradiction_penalty(
    event: Event,
    profile: Profile,
    current_themes: dict[str, float],
) -> dict[str, float]:
    penalties = {theme: 0.0 for theme in THEMES}
    for theme in event.contradiction_targets:
        if theme not in penalties:
            continue
        current = current_themes.get(theme, 0.0)
        penalties[theme] = round(profile.contradiction_damping * (0.15 + 0.35 * current), 4)
    return penalties


def update_themes(
    current_themes: dict[str, float],
    charge_by_theme: dict[str, float],
    contradiction_by_theme: dict[str, float],
    profile: Profile,
) -> dict[str, float]:
    updated: dict[str, float] = {}
    for theme in THEMES:
        decayed = current_themes.get(theme, 0.0) * (1.0 - profile.decay)
        charged = decayed + charge_by_theme.get(theme, 0.0) - contradiction_by_theme.get(theme, 0.0)
        capped = _clamp(charged, 0.0, profile.saturation_caps[theme])
        updated[theme] = round(capped, 4)
    return updated


def update_field(
    current_field: dict[str, float],
    event_tags: dict[str, float],
    theme_totals: dict[str, float],
) -> dict[str, float]:
    new_field = dict(current_field)
    total = sum(theme_totals.values())
    if total > 0:
        normalized_themes = {theme: theme_totals[theme] / total for theme in THEMES}
    else:
        normalized_themes = {theme: 0.0 for theme in THEMES}

    theme_tag_push: dict[str, float] = {}
    for theme, strength in normalized_themes.items():
        for tag, weight in THEME_TO_FIELD_TAGS[theme].items():
            theme_tag_push[tag] = theme_tag_push.get(tag, 0.0) + strength * weight

    for tag in set(current_field) | set(event_tags) | set(theme_tag_push):
        prior = current_field.get(tag, 0.0)
        event_value = event_tags.get(tag, 0.0)
        theme_value = theme_tag_push.get(tag, 0.0)
        blended = (0.55 * prior) + (0.3 * event_value) + (0.15 * theme_value)
        new_field[tag] = round(_clamp(blended, 0.0, 1.0), 4)
    return new_field


def derive_forward_bias(theme_totals: dict[str, float]) -> dict[str, object]:
    total = sum(theme_totals.values())
    if total > 0:
        normalized = {theme: round(theme_totals[theme] / total, 4) for theme in THEMES}
    else:
        normalized = {theme: 0.0 for theme in THEMES}

    ranked = sorted(THEMES, key=lambda theme: (-theme_totals[theme], theme))
    dominant = ranked[0]
    return {
        "normalized_theme_strengths": normalized,
        "dominant_theme": dominant,
        "ranked_themes": ranked,
    }


def summarize_interpretation(run: RunTrace) -> str:
    first = run.steps[0].dominant_theme if run.steps else run.final_dominant_theme
    final = run.final_dominant_theme
    changed = first != final

    if run.stream_name == "break":
        if changed and final == "return":
            return "Profile revised toward return under contradiction pressure."
        if final == "return":
            return "Profile held to return as corrective evidence accumulated."
        return "Profile retained earlier tension despite corrective evidence."

    if changed:
        return f"Profile drifted from {first} toward {final} as the stream accumulated."
    if final == "warning":
        return "Profile converged toward warning despite mixed evidence."
    if final == "return":
        return "Profile converged toward return from ambiguous cues."
    return "Profile converged toward loss under unresolved gaps and silence."


def run_stream_for_profile(events: list[Event], profile: Profile, stream_name: str) -> RunTrace:
    current_field = dict(profile.initial_field)
    current_themes = dict(profile.initial_themes)
    steps: list[StepTrace] = []

    for event in events:
        overlap_by_theme = overlap(event, current_field)
        charge_by_theme = {
            theme: round(profile.coupling_gain * profile.state_weight * overlap_by_theme[theme], 4)
            for theme in THEMES
        }
        contradiction_by_theme = contradiction_penalty(event, profile, current_themes)
        current_themes = update_themes(current_themes, charge_by_theme, contradiction_by_theme, profile)
        current_field = update_field(current_field, event.tags, current_themes)
        forward_bias = derive_forward_bias(current_themes)

        steps.append(
            StepTrace(
                profile_name=profile.name,
                stream_name=stream_name,
                event_id=event.id,
                event_label=event.label,
                event_tags=_round_map(event.tags),
                theme_hints=_round_map(event.theme_hints),
                overlap_by_theme=overlap_by_theme,
                charge_by_theme=charge_by_theme,
                contradiction_by_theme=contradiction_by_theme,
                theme_totals_after_update=current_themes,
                dominant_theme=forward_bias["dominant_theme"],
                forward_bias=forward_bias,
                field_snapshot=_round_map(current_field),
            )
        )

    final_bias = derive_forward_bias(current_themes)
    run = RunTrace(
        profile_name=profile.name,
        stream_name=stream_name,
        steps=steps,
        final_theme_totals=current_themes,
        final_dominant_theme=final_bias["dominant_theme"],
    )
    run.interpretation_summary = summarize_interpretation(run)
    return run


def run_demo(stream_name: str) -> dict[str, list[RunTrace]]:
    profiles = load_profiles(DATA_DIR / "profiles.json")
    stream_map = {
        "neutral": load_events(DATA_DIR / "events_neutral.json"),
        "break": load_events(DATA_DIR / "events_break.json"),
    }

    if stream_name == "all":
        selected = stream_map
    else:
        selected = {stream_name: stream_map[stream_name]}

    return {
        stream: [run_stream_for_profile(events, profile, stream) for profile in profiles]
        for stream, events in selected.items()
    }
