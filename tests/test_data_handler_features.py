"""Unit tests for DataHandler validation, load_from_string, and export_to_json_string."""

import json
import pytest
from core.graph import SocialGraph
from core.user_manager import UserManager
from utils.data_handler import DataHandler


def test_validate_network_data_valid():
    data = {
        "users": [
            {"id": "1", "name": "Alice", "username": "alice", "branch": "CSE", "year": 2, "interests": ["coding"]},
            {"id": "2", "name": "Bob", "username": "bob", "branch": "ECE", "year": 2, "interests": ["gaming"]},
        ],
        "friendships": [["1", "2"]],
    }
    is_valid, errors = DataHandler.validate_network_data(data)
    assert is_valid is True
    assert errors == []


def test_validate_network_data_invalid_structure():
    is_valid, errors = DataHandler.validate_network_data("not a dict")
    assert is_valid is False
    assert len(errors) > 0


def test_validate_network_data_duplicate_username():
    data = {
        "users": [
            {"id": "1", "name": "Alice", "username": "shared_un"},
            {"id": "2", "name": "Bob", "username": "shared_un"},
        ],
        "friendships": [],
    }
    is_valid, errors = DataHandler.validate_network_data(data)
    assert is_valid is False
    assert any("Duplicate username" in e for e in errors)


def test_validate_network_data_unknown_id_in_friendship():
    data = {
        "users": [{"id": "1", "name": "Alice"}],
        "friendships": [["1", "99"]],
    }
    is_valid, errors = DataHandler.validate_network_data(data)
    assert is_valid is False
    assert any("unknown user ID '99'" in e for e in errors)


def test_validate_network_data_self_friendship():
    data = {
        "users": [{"id": "1", "name": "Alice"}],
        "friendships": [["1", "1"]],
    }
    is_valid, errors = DataHandler.validate_network_data(data)
    assert is_valid is False
    assert any("Self-friendship disallowed" in e for e in errors)


def test_load_from_string_round_trip():
    original_data = {
        "users": [
            {"id": "1", "name": "Alice", "username": "alice", "branch": "CSE", "year": 2, "interests": ["coding"]},
            {"id": "2", "name": "Bob", "username": "bob", "branch": "IT", "year": 3, "interests": ["music"]},
        ],
        "friendships": [["1", "2"]],
    }
    json_str = json.dumps(original_data)
    um, sg, errors = DataHandler.load_from_string(json_str)
    assert errors == []
    assert um.get_user_count() == 2
    assert sg.are_friends("1", "2") is True
    assert um.get_user("1")["username"] == "alice"

    exported = DataHandler.export_to_json_string(um, sg)
    parsed = json.loads(exported)
    assert len(parsed["users"]) == 2
    assert parsed["friendships"] == [["1", "2"]]
