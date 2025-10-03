import pytest
from unittest.mock import MagicMock
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data
from constants import PLAYERS, GAMES

def test_fetch_all():
    mock_table = MagicMock()
    mock_table.scan.return_value = {'Items': [{'id':'1'}, {'id':'2'}]}
    result = data.fetch_all(mock_table)
    assert len(result) == 2

def test_save_score():
    mock_table = MagicMock()
    parsed_data = {
        'raw_game': 'Pinpoint',
        'game_number': 42,
        'scores': [5, 95],
        'units': ['guesses', '%']
    }
    result = data.save_score(mock_table, 'Mikuś', parsed_data, game_date='03-10-2025')
    assert result['user_id'] == 'Mikuś'
    assert result['scores'] == [5,95]
    assert result['units'] == ['guesses','%']
    assert result['game_date'] == '03-10-2025'

def test_invalid_user_and_game():
    mock_table = MagicMock()
    parsed_data = {
        'raw_game': 'Pinpoint',
        'game_number': 1,
        'scores':[5],
        'units':['guesses']
    }
    with pytest.raises(ValueError):
        data.save_score(mock_table, 'InvalidUser', parsed_data)
    parsed_data_invalid_game = parsed_data.copy()
    parsed_data_invalid_game['raw_game'] = 'InvalidGame'
    with pytest.raises(ValueError):
        data.save_score(mock_table, 'Mikuś', parsed_data_invalid_game)

def test_generate_test_data():
    """Test generating test data for multiple days with explicit game_date"""
    mock_table = MagicMock()
    fixed_date = '03-10-2025'

    result = data.generate_test_data(
        table=mock_table,
        user='Mikuś',
        game='Pinpoint',
        start_day=1,
        end_day=3,
        game_date=fixed_date
    )
    assert result is True
    # Should generate one item per day
    assert mock_table.put_item.call_count == 3
    # Check first item
    first_item = mock_table.put_item.call_args_list[0][1]['Item']
    assert first_item['user_id'] == 'Mikuś'
    assert first_item['raw_game'] == 'Pinpoint'
    assert first_item['game_date'] == fixed_date
    assert 'scores' in first_item
    assert 'units' in first_item

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
