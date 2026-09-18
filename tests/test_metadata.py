"""Contract tests for repository metadata, discoverability, bilingual parity, CI workflows, and runtime invariants."""

import json
import re
import tomllib
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
        "tests-31%20passed",
        "zero%20egress",
        "AgentEvent%20v2",
        "cell%20%7C%20fork--master",
    ]
    for badge in required_badges_en:
        assert badge in readme_en, f"Badge component '{badge}' missing in README.md"

    required_badges_de = [
        "python-3.10+",
        "Lizenz-MIT",
        "tests-31%20bestanden",
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


def test_mermaid_diagrams_syntax_and_quoting():
    """Verify Mermaid diagrams in README files adhere to quoting rules and avoid statement terminators."""
    for filename in ["README.md", "README_de.md"]:
        text = (ROOT / filename).read_text(encoding="utf-8")
        blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", text, re.DOTALL)
        assert len(blocks) >= 2, f"Expected at least 2 Mermaid diagrams in {filename}, found {len(blocks)}"

        for block in blocks:
            if "sequenceDiagram" in block:
                # In sequence diagrams, no semicolons as line terminators
                for line in block.splitlines():
                    trimmed = line.strip()
                    if trimmed and not trimmed.startswith("%%"):
                        assert not trimmed.endswith(";"), f"Statement terminator ';' in sequence diagram line: {line}"
            if "flowchart" in block or "graph" in block:
                # Ensure labels with parentheses are properly quoted
                for line in block.splitlines():
                    if "(" in line and ")" in line and "-->" in line:
                        # Edge or node with parens must have quotes
                        assert '"' in line or "'" in line or "|" in line, f"Unquoted parens in flowchart line: {line}"



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


def test_manifest_consistency_and_pyproject_urls():
    """Verify version parity across manifests, PEP 621 URLs, and llms.txt recency."""
    pyproject_path = ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    version = pyproject["project"]["version"]
    assert version == "1.0.3", f"Expected version 1.0.3 in pyproject.toml, found {version}"

    urls = pyproject["project"].get("urls", {})
    expected_urls = [
        "Homepage",
        "Documentation",
        "Repository",
        "Issues",
        "Bug Tracker",
        "Changelog",
        "Security",
        "Third-Party Licenses",
        "Parent Organization",
        "Umbrella Ecosystem",
        "Marketing Log",
        "LLM Ready",
    ]
    for key in expected_urls:
        assert key in urls, f"Missing URL key '{key}' in pyproject.toml"

    # Module manifest parity
    module_path = ROOT / "ellmos-module.v2.json"
    with open(module_path, "r", encoding="utf-8") as f:
        module_data = json.load(f)
    assert module_data.get("version") == version, "Version mismatch in ellmos-module.v2.json"

    # llms.txt parity
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert f"Version: {version}" in llms_text
    assert "Last-checked: 2026-09-18" in llms_text

    # CHANGELOG parity
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{version}] - 2026-09-18" in changelog_text


def test_ci_workflows_concurrency_timeouts_permissions():
    """Verify GitHub Actions workflows have least-privilege permissions, concurrency control, and timeouts."""
    workflows_dir = ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir(), ".github/workflows directory must exist"

    ci_file = workflows_dir / "ci.yml"
    stale_file = workflows_dir / "stale.yml"
    welcome_file = workflows_dir / "welcome.yml"

    assert ci_file.is_file(), "ci.yml must exist"
    assert stale_file.is_file(), "stale.yml must exist"
    assert welcome_file.is_file(), "welcome.yml must exist"

    ci_content = ci_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in ci_content
    assert "timeout-minutes: 15" in ci_content
    assert "permissions:" in ci_content
    assert "contents: read" in ci_content
    for py_ver in ["3.10", "3.11", "3.12", "3.13"]:
        assert py_ver in ci_content
    assert "ubuntu-latest" in ci_content
    assert "windows-latest" in ci_content

    stale_content = stale_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in stale_content
    assert "timeout-minutes: 10" in stale_content
    assert "actions/stale@v9" in stale_content
    assert "issues: write" in stale_content
    assert "pull-requests: write" in stale_content

    welcome_content = welcome_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in welcome_content
    assert "timeout-minutes: 5" in welcome_content
    assert "actions/first-interaction@v3" in welcome_content
    assert "issues: write" in welcome_content


def test_gitignore_multihost_and_locks():
    """Verify .gitignore contains patterns for multi-host sync conflicts, system locks, and cache artifacts."""
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file(), ".gitignore must exist"
    content = gitignore_path.read_text(encoding="utf-8")

    # Multi-host sync patterns
    assert "*conflicted copy*" in content
    assert "*-ASUS*" in content
    assert "*-WORKSTATION*" in content

    # Systemwide lock coordination
    assert "LOCK" in content
    assert "LOCK.permissions.json" in content
    assert "LOCK.user.*" in content

    # Build & tool caches
    assert "uv.lock" in content
    assert ".pytest_cache/" in content
    assert "*.db-wal" in content


def test_pep621_metadata_and_pytest_config():
    """Verify PEP 621 packaging metadata and pytest configuration options."""
    pyproject_path = ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    # Build system
    assert "build-system" in pyproject
    assert "setuptools.build_meta" in pyproject["build-system"]["build-backend"]

    # License files
    license_files = pyproject["project"].get("license-files", [])
    assert "LICENSE" in license_files
    assert "THIRD_PARTY_LICENSES.md" in license_files

    # Pytest configuration
    pytest_cfg = pyproject["tool"]["pytest"]["ini_options"]
    assert pytest_cfg.get("minversion") == "7.0"
    norecursedirs = pytest_cfg.get("norecursedirs", [])
    for d in ["_results", "_sources", "out", "data"]:
        assert d in norecursedirs, f"Expected '{d}' in pytest norecursedirs"


def test_statutory_notice_and_utf8_integrity():
    """Verify § 521 BGB statutory liability notice and clean UTF-8 encoding across docs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "§ 521 BGB" in readme_en
    assert "§ 521 BGB" in readme_de
    assert "Statutory Notice" in readme_en
    assert "Gesetzlicher Hinweis" in readme_de
    assert "Vorsatz und grobe Fahrlässigkeit" in readme_de

    # UTF-8 integrity check across tracked text files
    for ext in ["*.md", "*.py", "*.json", "*.toml", "*.txt"]:
        for file in ROOT.glob(ext):
            try:
                file.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                assert False, f"File {file.name} failed UTF-8 decode: {exc}"


def test_third_party_licenses_and_security():
    """Verify license audit, runtime invariants, and security response policy."""
    lic_file = ROOT / "THIRD_PARTY_LICENSES.md"
    sec_file = ROOT / "SECURITY.md"

    assert lic_file.exists(), "THIRD_PARTY_LICENSES.md must exist"
    assert sec_file.exists(), "SECURITY.md must exist"

    lic_text = lic_file.read_text(encoding="utf-8")
    assert "PSF-2.0" in lic_text
    assert "MIT" in lic_text
    assert "Zero Copyleft Contamination" in lic_text
    assert "RunAsInvoker" in lic_text
    assert "Stand:** 2026-09-18" in lic_text
    assert "Version:** 1.0.3" in lic_text

    sec_text = sec_file.read_text(encoding="utf-8")
    assert "48" in sec_text, "48h SLA missing in SECURITY.md"


def test_marketing_log_recency():
    """Verify that repo-local MARKETING-LOG.txt is present and documents Release 1.0.3."""
    marketing_log = ROOT / "MARKETING-LOG.txt"
    assert marketing_log.is_file(), "MARKETING-LOG.txt must exist"

    content = marketing_log.read_text(encoding="utf-8")
    assert "Release 1.0.3" in content
    assert "2026-09-18" in content
    assert "Pfad A" in content
