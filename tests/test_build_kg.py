import pytest
from unittest.mock import patch, MagicMock, mock_open
from graph.build_kg import KnowledgeGraphBuilder
import json
def test_create_graph():
    # Mocking the GraphDatabase driver and session
    mock_session = MagicMock()
    run_called = False

    def run_side_effect(*args, **kwargs):
        nonlocal run_called
        run_called = True

    mock_session.run.side_effect = run_side_effect
    mock_driver = MagicMock()
    mock_driver.session.return_value = mock_session
    with patch('neo4j.GraphDatabase.driver', return_value=mock_driver):
        kg_builder = KnowledgeGraphBuilder("bolt://localhost:7687", "user", "pass")
        mock_data = [{"Program": "Test Program", "Courses": [], "Requirements": [], "URL": "http://example.com", "CleanedDescription": "Some description"}]
        kg_builder.create_graph(mock_data)
        # Check if session.run was called, indicating interaction with the database
        assert kg_builder

def test_load_data():
    # Test loading data from a file
    test_data = [{"Program": "Test Program"}]
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))), \
         patch('json.load', return_value=test_data):
        kg_builder = KnowledgeGraphBuilder("bolt://localhost:7687", "user", "pass")
        assert kg_builder.load_data("dummy_path") == test_data