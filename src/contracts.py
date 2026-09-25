"""버전별 Signal 계약을 선택해 엔진 진입 전에 검증한다."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

SIGNAL_SCHEMA_VERSION = 1


def validate_signals(
    signals: Sequence[Mapping[str, Any]],
    validators: Mapping[int, Draft202012Validator],
) -> None:
    """각 Signal의 schema_version에 맞는 계약으로 검증한다."""
    for index, signal in enumerate(signals):
        value = signal.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not isfinite(value):
                raise ValidationError(f"signal[{index}] value must be finite")
        version = signal.get("schema_version")
        validator = validators.get(version) if isinstance(version, int) else None
        if validator is None:
            raise ValidationError(
                f"signal[{index}] has unsupported schema_version: {version!r}"
            )
        validator.validate(signal)
