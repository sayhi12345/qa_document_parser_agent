import pytest
from modules.figma_client import extract_file_key, FigmaMCPClient


class TestExtractFileKey:
    def test_valid_file_url(self):
        """Test extracting file key from valid file URL."""
        url = "https://www.figma.com/file/ABC123XYZ/MyDesign"
        result = extract_file_key(url)
        assert result == "ABC123XYZ"

    def test_valid_design_url(self):
        """Test extracting file key from valid design URL."""
        url = "https://www.figma.com/design/DEF456UVW/AnotherDesign"
        result = extract_file_key(url)
        assert result == "DEF456UVW"

    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        url = "https://www.figma.com/file/GHI789RST/Design?node-id=1:2"
        result = extract_file_key(url)
        assert result == "GHI789RST"

    def test_url_with_hash(self):
        """Test URL with hash fragment."""
        url = "https://www.figma.com/file/JKL012MNO/Design#section"
        result = extract_file_key(url)
        assert result == "JKL012MNO"

    def test_invalid_url(self):
        """Test with invalid URL."""
        url = "https://www.google.com"
        result = extract_file_key(url)
        assert result is None

    def test_malformed_figma_url(self):
        """Test with malformed Figma URL."""
        url = "https://www.figma.com/other/ABC123"
        result = extract_file_key(url)
        assert result is None

    def test_empty_string(self):
        """Test with empty string."""
        result = extract_file_key("")
        assert result is None

    def test_url_encoded_characters(self):
        """Test with URL-encoded characters in design name."""
        url = "https://www.figma.com/file/XYZ789ABC/%E6%B4%BB%E5%8B%95%E8%AA%AA%E6%98%8E"
        result = extract_file_key(url)
        assert result == "XYZ789ABC"


class TestFigmaMCPClient:
    def test_init_with_valid_token(self):
        """Test initialization with valid token."""
        client = FigmaMCPClient(access_token="test_token_123")
        assert client.access_token == "test_token_123"
        assert client.base_url == "https://api.figma.com/v1"
        assert client.session is not None
        assert client.session.headers["X-FIGMA-TOKEN"] == "test_token_123"
        assert client.session.headers["Accept"] == "application/json"

    def test_init_with_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = FigmaMCPClient(
            access_token="test_token",
            base_url="https://custom.api.com/v2"
        )
        assert client.base_url == "https://custom.api.com/v2"

    def test_init_without_token_raises_error(self):
        """Test that initialization without token raises ValueError."""
        with pytest.raises(ValueError, match="FIGMA_ACCESS_TOKEN 未提供"):
            FigmaMCPClient(access_token="")

    def test_init_with_none_token_raises_error(self):
        """Test that initialization with None token raises ValueError."""
        with pytest.raises(ValueError, match="FIGMA_ACCESS_TOKEN 未提供"):
            FigmaMCPClient(access_token=None)

    def test_fetch_file_success(self, mocker):
        """Test successful file fetch."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "document": {"type": "DOCUMENT", "name": "Test"}
        }
        
        mock_session = mocker.Mock()
        mock_session.get.return_value = mock_response
        
        client = FigmaMCPClient(access_token="test_token")
        client.session = mock_session
        
        result = client.fetch_file("ABC123")
        
        mock_session.get.assert_called_once_with(
            "https://api.figma.com/v1/files/ABC123",
            timeout=30
        )
        assert result == {"document": {"type": "DOCUMENT", "name": "Test"}}

    def test_fetch_file_error_response(self, mocker):
        """Test file fetch with error response."""
        mock_response = mocker.Mock()
        mock_response.status_code = 403
        mock_response.text = "Access denied"
        
        mock_session = mocker.Mock()
        mock_session.get.return_value = mock_response
        
        client = FigmaMCPClient(access_token="test_token")
        client.session = mock_session
        
        with pytest.raises(RuntimeError, match="Figma API 回傳狀態碼 403"):
            client.fetch_file("ABC123")

    def test_fetch_file_with_custom_base_url(self, mocker):
        """Test file fetch with custom base URL."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"document": {}}
        
        mock_session = mocker.Mock()
        mock_session.get.return_value = mock_response
        
        client = FigmaMCPClient(
            access_token="test_token",
            base_url="https://custom.api.com"
        )
        client.session = mock_session
        
        client.fetch_file("XYZ789")
        
        mock_session.get.assert_called_once_with(
            "https://custom.api.com/files/XYZ789",
            timeout=30
        )
