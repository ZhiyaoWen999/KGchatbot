import pytest
from unittest.mock import mock_open, patch
from Preprocess_data.data_preprocess import CourseDataProcessor
import json
def test_clean_text():
    processor = CourseDataProcessor('input.json', 'output.json')
    input_text = "This is a sample text with UCL menu London, Bloomsbury. Some symbols: !@#$%^&*()"
    expected_output = "sample text ucl menu london bloomsbury symbols"
    assert processor.clean_text(input_text) == expected_output

def test_process():
    # Mocking load_data and save_data
    mock_data = [
        {"Description": "Sample description about UCL menu London, Bloomsbury. More text."}
    ]
    with patch('json.load', return_value=mock_data), \
         patch('json.dump') as mock_dump:
        processor = CourseDataProcessor('data/input.json', 'data/output.json')
        processor.process()
        mock_dump.assert_called_once()