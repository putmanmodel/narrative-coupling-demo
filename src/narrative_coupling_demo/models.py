from __future__ import annotations

from dataclasses import asdict, dataclass, field


THEMES = ("warning", "return", "loss")


@dataclass(slots=True)
class Event:
    id: str
    label: str
    tags: dict[str, float]
    theme_hints: dict[str, float]
    contradiction_targets: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class Profile:
    name: str
    coupling_gain: float
    decay: float
    contradiction_damping: float
    saturation_caps: dict[str, float]
    state_weight: float
    initial_field: dict[str, float]
    initial_themes: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class StepTrace:
    profile_name: str
    stream_name: str
    event_id: str
    event_label: str
    event_tags: dict[str, float]
    theme_hints: dict[str, float]
    overlap_by_theme: dict[str, float]
    charge_by_theme: dict[str, float]
    contradiction_by_theme: dict[str, float]
    theme_totals_after_update: dict[str, float]
    dominant_theme: str
    forward_bias: dict[str, object]
    field_snapshot: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class RunTrace:
    profile_name: str
    stream_name: str
    steps: list[StepTrace] = field(default_factory=list)
    final_theme_totals: dict[str, float] = field(default_factory=dict)
    final_dominant_theme: str = ""
    interpretation_summary: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_name": self.profile_name,
            "stream_name": self.stream_name,
            "steps": [step.to_dict() for step in self.steps],
            "final_theme_totals": self.final_theme_totals,
            "final_dominant_theme": self.final_dominant_theme,
            "interpretation_summary": self.interpretation_summary,
        }
