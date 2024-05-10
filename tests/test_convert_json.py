import pytest
from unittest.mock import patch, mock_open
from Preprocess_data.covert_json import load_data, transform_data, save_data, main
import json
def test_transform_data():
    input_data = [{"title": "Course 1", "url": "http://example.com", "paragraphs": ["This is a course.", "It covers modules."] }]
    expected_output = [{"Program": "Course 1", "URL": "http://example.com", "Description": "This is a course.", "Requirements": "", "Courses": "It covers modules."}]
    assert transform_data(input_data) 

def test_main_integration():
    # Integrating load, transform, and save functions
    with patch('Preprocess_data.covert_json.load_data', return_value=[{"title": "Course 1"}]), \
         patch('Preprocess_data.covert_json.transform_data', return_value=[{"Program": "Course 1"}]), \
         patch('Preprocess_data.covert_json.save_data') as mock_save:
        main()
        mock_save.assert_called_once_with([{"Program": "Course 1"}], 'data/transformed_course_info.json')

@pytest.mark.parametrize("filepath, expected", [
    ("data/course_info.json", [{"title": "Test Course"}])
])
def test_load_data(filepath, expected):
    with patch('builtins.open', mock_open(read_data=json.dumps(expected))):
        assert load_data(filepath) == expected