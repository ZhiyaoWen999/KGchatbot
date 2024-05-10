import pytest
from unittest.mock import patch, MagicMock, mock_open
import requests
from Preprocess_data.crawler import UCLCourseScraper

@pytest.fixture
def scraper():
    return UCLCourseScraper()

def test_fetch_course_urls_success(scraper):
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = '<a href="https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/course-1">Course 1</a>'
        mock_get.return_value = mock_response
        
        with patch('builtins.open', mock_open()) as mock_file:
            scraper.fetch_course_urls()
            # Check if the URL was extracted correctly
            mock_file().write.assert_called_with("https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/course-1\n")

def test_fetch_course_info_failure(scraper):
    with patch('requests.get') as mock_get:

        mock_get.side_effect = requests.exceptions.Timeout
        result = scraper.fetch_course_info("https://www.ucl.ac.uk/non-existent-course")
        assert result is None
        mock_get.assert_called_with("https://www.ucl.ac.uk/non-existent-course", timeout=10)

def test_crawl_course_pages(scraper):
    with patch.object(scraper, 'fetch_course_info', return_value={'url': 'some_url', 'title': 'Some Title', 'paragraphs': ['Introduction']}) as mock_fetch_info:
        with patch('builtins.open', mock_open(read_data="some_url\n")) as mock_file:
            with patch('json.dump') as mock_json_dump:
                scraper.crawl_course_pages()
                mock_fetch_info.assert_called()
                mock_json_dump.assert_called_once() 

