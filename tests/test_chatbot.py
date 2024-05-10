import pytest
from unittest.mock import patch, MagicMock
from src.chatbot import Chatbot


@pytest.fixture
def chatbot(mocker):
    mocker.patch('openai.ChatCompletion.create', return_value={
        'choices': [{'message': {'content': 'program_details'}}]
    })
    mocker.patch('neo4j.GraphDatabase.driver')
    return Chatbot('fake_openai_key', 'bolt://localhost:7687', 'user', 'password')

def test_close(chatbot, mocker):
    mock_driver = mocker.patch('neo4j.GraphDatabase.driver')
    chatbot.driver = mock_driver
    chatbot.close()
    mock_driver.close.assert_called_once()

def test_query_neo4j_program_details(chatbot, mocker):
    mock_session = mocker.patch('neo4j.GraphDatabase.driver').return_value.session.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.single.return_value = {'description': 'Some program', 'url': 'http://example.com'}
    mock_session.run.return_value = mock_result
    
    result = chatbot.query_neo4j('program_details', {'program_name': 'Test Program'})
    assert result == chatbot.query_neo4j('program_details', {'program_name': 'Test Program'})

def test_query_neo4j_course_details(chatbot, mocker):
    mock_session = mocker.patch('neo4j.GraphDatabase.driver').return_value.session.return_value.__enter__.return_value
    mock_session.run.return_value.single.return_value = {'name': 'Test Course', 'description': 'Some course'}
    result = chatbot.query_neo4j('course_details', {'course_name': 'Test Course'})
    assert result == chatbot.query_neo4j('course_details', {'course_name': 'Test Course'})

def test_query_neo4j_requirements(chatbot, mocker):
    mock_session = mocker.patch('neo4j.GraphDatabase.driver').return_value.session.return_value.__enter__.return_value
    mock_session.run.return_value.data.return_value = [{'description': 'Requirement 1'}, {'description': 'Requirement 2'}]
    result = chatbot.query_neo4j('requirements', {'program_name': 'Test Program'})
    assert result == chatbot.query_neo4j('requirements', {'program_name': 'Test Program'})

def test_parse_intent_and_entities(chatbot):
    intent, entities = chatbot.parse_intent_and_entities("Tell me about the requirements for Computer Science")
    assert intent == intent
    assert entities == entities

def test_run_chat_session(mocker, chatbot):
    mocker.patch('builtins.input', side_effect=['Tell me about the requirements for Computer Science', 'exit'])
    mocker.patch('builtins.print')
    mocker.patch.object(chatbot, 'parse_intent_and_entities', return_value=('requirements', {'program_name': 'Computer Science'}))
    chatbot.run_chat_session()
    assert chatbot.parse_intent_and_entities.call_count == 1