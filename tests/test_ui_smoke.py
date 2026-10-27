"""Smoke tests for Streamlit pages using streamlit.testing.v1.AppTest."""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def test_app_entrypoint_smoke():
    """Verify app.py loads without crashing."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_dashboard_page_smoke():
    """Verify Dashboard page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "1_Dashboard.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_recommendations_page_smoke():
    """Verify Recommendations page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "2_Recommendations.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_path_finder_page_smoke():
    """Verify Path Finder page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "3_Path_Finder.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_bfs_visualizer_page_smoke():
    """Verify BFS Visualizer page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "4_BFS_Visualizer.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_hash_lab_page_smoke():
    """Verify Hash Lab page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "5_Hash_Lab.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_network_editor_page_smoke():
    """Verify Network Editor page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "6_Network_Editor.py"), default_timeout=15)
    at.run()
    assert not at.exception


def test_theory_and_viva_page_smoke():
    """Verify Theory & Viva page executes with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "pages" / "7_Theory_and_Viva.py"), default_timeout=15)
    at.run()
    assert not at.exception
