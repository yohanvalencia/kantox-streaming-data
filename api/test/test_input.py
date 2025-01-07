import json
import pytest
from random import randrange
from unittest.mock import patch, MagicMock
from pipeline import input

@pytest.fixture
def mock_producer(mocker):
    mock_producer_instance = mocker.patch("pipeline.input.Producer", autospec=True)
    mock_producer_instance.return_value.produce = MagicMock()
    mock_producer_instance.return_value.flush = MagicMock()
    return mock_producer_instance


@patch("pipeline.input.Producer")
def test_collect_error(mock_producer):
    result = input.collect({
        'id': randrange(0, 999999),
        'type': 'page_view',
        "event": {
            'user-agent': 'Mozilla/5.0 (Linux; Android 2.2) AppleWebKit/536.2 (KHTML, like Gecko) Chrome/46.0.817.0 Safari/536.2',
            'ip': '24.49.160.149',
            'customer-id': None,
            'timestamp': '2022-05-25T05:44:03.648681',
            'page': 'https://xcc-webshop.com/category/13'
        }
    })
    assert result == {"status": "error", "message": "Payload must be a JSON array."}
    mock_producer.return_value.produce.assert_not_called()

@patch("pipeline.input.Producer")
def test_collect_ok(mock_producer):
    result = input.collect([{
        'id': randrange(0, 999999),
        'type': 'page_view',
        "event": {
            'user-agent': 'Mozilla/5.0 (Linux; Android 2.2) AppleWebKit/536.2 (KHTML, like Gecko) Chrome/46.0.817.0 Safari/536.2',
            'ip': '24.49.160.149',
            'customer-id': None,
            'timestamp': '2022-05-25T05:44:03.648681',
            'page': 'https://xcc-webshop.com/category/13'
        }
    }])
    assert result == {"status": "OK"}

@patch("pipeline.input.avro_serializer")
@patch("pipeline.input.Producer")
def test_collect_error(mock_producer, mock_avro_serializer):
    mock_avro_serializer.side_effect = Exception("Serialization failed")

    mock_producer_instance = MagicMock()
    mock_producer.return_value = mock_producer_instance

    result = input.collect([{
        'id': randrange(0, 999999),
        'type': 'page_view',
        "event": {
            'user-agent': 'Mozilla/5.0 (Linux; Android 2.2) AppleWebKit/536.2 (KHTML, like Gecko) Chrome/46.0.817.0 Safari/536.2',
            'ip': '24.49.160.149',
            'customer-id': None,
            'timestamp': '2022-05-25T05:44:03.648681',
            'page': 'https://xcc-webshop.com/category/13'
        }
    }])

    assert result == {"status": "OK"}
    mock_avro_serializer.assert_called_once()
