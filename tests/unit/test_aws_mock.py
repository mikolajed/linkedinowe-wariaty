import pytest
from unittest.mock import MagicMock, patch
from utils import aws

# ----------------------------
# Test AWS table with credentials
# ----------------------------
def test_get_ddb_table_with_credentials():
    aws_cfg = {
        'access_key_id': 'valid_test_key',
        'secret_access_key': 'valid_test_secret',
        'region': 'eu-north-1'
    }

    mock_table = MagicMock()
    mock_ddb = MagicMock()
    mock_ddb.Table.return_value = mock_table
    mock_session = MagicMock()
    mock_session.resource.return_value = mock_ddb

    with patch('boto3.Session', return_value=mock_session) as mock_sess:
        result = aws.get_ddb_table(aws_cfg, 'test_table')
        assert result == mock_table
        mock_sess.assert_called_once_with(
            aws_access_key_id='valid_test_key',
            aws_secret_access_key='valid_test_secret',
            region_name='eu-north-1'
        )
        mock_session.resource.assert_called_once_with("dynamodb")
        mock_ddb.Table.assert_called_once_with("test_table")

# ----------------------------
# Test mock table without credentials
# ----------------------------
def test_get_ddb_table_without_credentials():
    aws_cfg = {}
    with patch('streamlit.warning') as mock_warning:
        result = aws.get_ddb_table(aws_cfg, 'test_table')
        # Verify methods exist
        assert hasattr(result, 'put_item')
        assert hasattr(result, 'scan')
        assert hasattr(result, 'delete_item')
        # Verify warning was shown
        mock_warning.assert_called_once_with(
            "No AWS credentials – using in-memory storage for test_table (data lost on restart)."
        )

# ----------------------------
# Test invalid credentials
# ----------------------------
def test_get_ddb_table_with_invalid_credentials():
    aws_cfg = {
        'access_key_id': 'invalid',
        'secret_access_key': 'invalid',
        'region': 'eu-north-1'
    }

    with patch('boto3.Session') as mock_session:
        mock_session.side_effect = Exception("Invalid credentials")
        result = aws.get_ddb_table(aws_cfg, 'test_table')
        assert result is None

# ----------------------------
# Test MockTable operations
# ----------------------------
def test_mock_table_operations():
    table = aws.get_ddb_table({}, 'test_table')

    # put_item
    item1 = {'user_id': '1', 'name': 'test1', 'timestamp': '2023-01-01'}
    table.put_item(Item=item1)
    
    # scan
    result = table.scan()
    assert len(result['Items']) == 1
    assert result['Items'][0] == item1

    # put_item with same key → overwrite
    item1_updated = {'user_id': '1', 'name': 'test1_updated', 'timestamp': '2023-01-01'}
    table.put_item(Item=item1_updated)
    result = table.scan()
    assert result['Items'][0]['name'] == 'test1_updated'

    # delete_item
    table.delete_item(Key={'user_id': '1', 'timestamp': '2023-01-01'})
    result = table.scan()
    assert len(result['Items']) == 0

# ----------------------------
# Run tests directly
# ----------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
