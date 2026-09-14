"""Contract tests for repository metadata, discoverability, bilingual parity, and runtime invariants."""

import re
import tomllib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_readme_bilingual_navigation_and_anchor_parity():
    """Verify that both READMEs have full 12-point quick navigation and matching section structures."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    en_nav = re.findall(r"^- \[(.+?)\]\(#(.+?)\)", readme_en, re.MULTILINE)
    de_nav = re.findall(r"^- \[(.+?)\]\(#(.+?)\)", readme_de, re.MULTILINE)

    assert len(en_nav) == 12, f"Expected 12 navigation items in README.md, found {len(en_nav)}"
    assert len(de_nav) == 12, f"Expected 12 navigation items in README_de.md, found {len(de_nav)}"

    # Check each anchor header exists in respective README
    for _, anchor in en_nav:
        assert anchor in readme_en, f"Anchor #{anchor} missing in README.md text"

    for _, anchor in de_nav:
        assert anchor in readme_de, f"Anchor #{anchor} missing in README_de.md text"


def test_readme_shields_badges():
    """Verify Shields.io badges in both README files."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    required_badges_en = [
        "python-3.10+",
        "License-MIT",
        "tests-25%20passed",
        "zero%20egress",
        "AgentEvent%20v2",
        "cell%20%7C%20fork--master",
    ]
    for badge in required_badges_en:
        assert badge in readme_en, f"Badge component '{badge}' missing in README.md"

    required_badges_de = [
        "python-3.10+",
        "Lizenz-MIT",
        "tests-25%20bestanden",
        "zero%20egress",
        "AgentEvent%20v2",
        "zellmodell%20%7C%20fork--master",
    ]
    for badge in required_badges_de:
        assert badge in readme_de, f"Badge component '{badge}' missing in README_de.md"


def test_readme_target_personas_and_seo():
    """Verify 4 target personas and SEO keywords in both languages."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    personas = ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]
    for persona in personas:
        assert persona in readme_en, f"Persona '{persona}' missing in README.md"
        assert persona in readme_de, f"Persona '{persona}' missing in README_de.md"

    assert "prompt archaeology" in readme_en.lower()
    assert "prompt-archäologie" in readme_de.lower()


def test_comparative_matrix_and_invariants():
    """Verify all 10 invariants INV-LOCAL-01 through INV-SLA-10 are present in comparative tables."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    invariants = [
        "INV-LOCAL-01",
        "INV-POSTHOC-02",
        "INV-DEPEND-03",
        "INV-SCHEMA-04",
        "INV-PIPELINE-05",
        "INV-TEMPLATE-06",
        "INV-PRIVACY-07",
        "INV-METRICS-08",
        "INV-FORMAT-09",
        "INV-SLA-10",
    ]

    for inv in invariants:
        assert inv in readme_en, f"Invariant '{inv}' missing in README.md matrix"
        assert inv in readme_de, f"Invariant '{inv}' missing in README_de.md matrix"


def test_third_party_licenses_and_security():
    """Verify license audit and security policy invariants."""
    lic_file = ROOT / "THIRD_PARTY_LICENSES.md"
    sec_file = ROOT / "SECURITY.md"

    assert lic_file.exists(), "THIRD_PARTY_LICENSES.md must exist"
    assert sec_file.exists(), "SECURITY.md must exist"

    lic_text = lic_file.read_text(encoding="utf-8")
    assert "PSF-2.0" in lic_text
    assert "MIT" in lic_text
    assert "Zero Copyleft Contamination" in lic_text
    assert "RunAsInvoker" in lic_text

    sec_text = sec_file.read_text(encoding="utf-8")
    assert "48" in sec_text, "48h SLA missing in SECURITY.md"


def test_manifest_consistency_and_pyproject_urls():
    """Verify version parity across manifests, PEP 621 URLs, and llms.txt recency."""
    pyproject_path = ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    version = pyproject["project"]["version"]
    assert version == "1.0.2", f"Expected version 1.0.2 in pyproject.toml, found {version}"

    urls = pyproject["project"].get("urls", {})
    assert "Repository" in urls
    assert "Documentation" in urls
    assert "Bug Tracker" in urls
    assert "Security" in urls
    assert "Marketing Log" in urls
    assert "Third-Party Licenses" in urls

    pytest_opts = pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "-ra -v" in pytest_opts.get("addopts", "")

    # Module manifest parity
    module_path = ROOT / "ellmos-module.v2.json"
    with open(module_path, "r", encoding="utf-8") as f:
        module_data = json.load(f)
    assert module_data.get("version") == version, "Version mismatch in ellmos-module.v2.json"

    # llms.txt parity
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert f"Version: {version}" in llms_text
    assert "Last-checked: 2026-09-14" in llms_text

    # CHANGELOG parity
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{version}] - 2026-09-14" in changelog_text
