"""Tests for the skill build's guardrails: edition blocks in shared docs, and the checks on what the Copilot edition says
(no advice it must never give, pointers that resolve, a SKILL.md line for every task guide)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_skill", ROOT / "tools" / "build_skill.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def test_editions_keep_their_own_blocks():
    text = ("shared\n<!-- portable,repo -->\npptxgenjs recipe\n<!-- /portable,repo -->\n"
            "<!-- copilot -->\nmv.office\n<!-- /copilot -->\nend\n")
    assert build.editions(text, "copilot") == "shared\nmv.office\nend\n"
    assert build.editions(text, "portable") == "shared\npptxgenjs recipe\nend\n"
    other = "<!-- note -->\nkept\n<!-- /note -->\n"                     # not an edition name: left alone
    assert build.editions(other, "copilot") == other


@pytest.fixture
def edition(tmp_path, monkeypatch):
    """A tiny Copilot edition with one task guide, wired into the build module."""
    guides = tmp_path / "guides"
    guides.mkdir()
    (guides / "review.md").write_text("# Reviewing\n", encoding="utf-8")
    out = tmp_path / "out"
    (out / "references").mkdir(parents=True)
    (out / "references" / "review.md").write_text("# Reviewing\nSee `references/rules.md`.\n", encoding="utf-8")
    (out / "references" / "rules.md").write_text("rules\n", encoding="utf-8")
    monkeypatch.setattr(build, "COPILOT_OUT", out)
    monkeypatch.setattr(build, "TASK_GUIDES", guides)

    def write(skill: str) -> Path:
        (out / "SKILL.md").write_text(skill, encoding="utf-8")
        return out
    return write


def test_a_clean_edition_passes(edition):
    edition("Feedback on a chart: `references/review.md`. Never `plt.savefig`; never PptxGenJS.\n")
    assert build.copilot_guidance() == []


def test_advice_the_copilot_edition_must_not_give(edition):
    out = edition("Feedback: `references/review.md`.\n")
    (out / "references" / "office.md").write_text("Build the deck with pptxgenjs.\nThen plt.savefig('a.png').\n"
                                                  "fig.show()  # Plotly is fine\n", encoding="utf-8")
    problems = build.copilot_guidance()
    assert any("office.md:1: names PptxGenJS" in p for p in problems)
    assert any("office.md:2: names matplotlib's savefig or show" in p for p in problems)
    assert not any("office.md:3" in p for p in problems)


def test_pointers_must_resolve_and_every_guide_needs_a_line(edition):
    edition("Read `references/options.md` first. Load `scripts/mck_setup.py`.\n")
    problems = build.copilot_guidance()
    assert "SKILL.md points to references/options.md, which isn't in the Copilot edition" in problems
    assert "SKILL.md points to scripts/mck_setup.py, which isn't in the Copilot edition" in problems
    assert "SKILL.md has no line pointing to the task guide references/review.md" in problems


def test_unfilled_placeholders(edition):
    edition("Feedback: `references/review.md`. Version {{version}}.\n")
    assert "SKILL.md: an unfilled {{placeholder}}" in build.copilot_guidance()
