"""Unit tests verifying that demo scripts fail safely in production."""

import os
import sys

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pytest
from scripts.seed_demo import check_not_production as check_seed_demo
from scripts.simulate_readings import check_not_production as check_simulate
from scripts.create_demo_events import check_not_production as check_demo_events


def test_seed_demo_rejects_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(SystemExit):
        check_seed_demo()


def test_simulate_readings_rejects_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(SystemExit):
        check_simulate()


def test_create_demo_events_rejects_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(SystemExit):
        check_demo_events()


def test_demo_scripts_allow_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    # Should not raise
    check_seed_demo()
    check_simulate()
    check_demo_events()
