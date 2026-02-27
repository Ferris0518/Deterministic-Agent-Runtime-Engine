from __future__ import annotations

from dare_framework.agent._internal.output_normalizer import build_output_envelope, normalize_run_output


def test_normalize_run_output_preserves_none_as_missing_text() -> None:
    assert normalize_run_output(None) is None


def test_build_output_envelope_uses_empty_content_for_missing_output() -> None:
    envelope = build_output_envelope(None)
    assert envelope["content"] == ""


def test_normalize_run_output_returns_none_for_dict_with_only_empty_text() -> None:
    assert normalize_run_output({"content": ""}) is None


def test_normalize_run_output_preserves_structured_fallback_when_non_text_fields_exist() -> None:
    normalized = normalize_run_output({"content": "", "error": "timeout"})
    assert normalized is not None
    assert '"error": "timeout"' in normalized
