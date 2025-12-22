import pytest
from unittest.mock import MagicMock, patch
from ingestion import DataIngestor
import requests

class TestDataIngestor:

    def test_sanitize_filename(self, temp_data_dir):
        """Test that filenames are cleaned of illegal chars."""
        ingestor = DataIngestor(str(temp_data_dir))
        
        raw_name = "Wiki: About/Page?"
        clean = ingestor._sanitize_filename(raw_name)
        assert clean == "Wiki_AboutPage"  # Expected based on regex: removes : / ? and replaces space
        
        assert ingestor._sanitize_filename("NormalFile") == "NormalFile"

    def test_extract_publish_date_wiki_footer(self, temp_data_dir):
        """Test date extraction from Paradox Wiki style footer."""
        ingestor = DataIngestor(str(temp_data_dir))
        
        html = """
        <html>
            <body>
                <div id="footer-info-lastmod"> This page was last edited on 22 December 2025, at 10:00.</div>
            </body>
        </html>
        """
        date = ingestor._extract_publish_date(html, "https://wiki.com/page")
        assert date == "2025-12-22"

    def test_extract_publish_date_fallback(self, temp_data_dir):
        """Test fallback to today's date if no metadata found."""
        ingestor = DataIngestor(str(temp_data_dir))
        html = "<html><body>Just text</body></html>"
        
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        date = ingestor._extract_publish_date(html, "http://example.com")
        assert date == today

    @patch('requests.get')
    def test_scrape_url_success(self, mock_get, temp_data_dir):
        """Test successful scraping of a fake page."""
        ingestor = DataIngestor(str(temp_data_dir))
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><title>Test Page</title><body><p>Hello World</p></body></html>"
        mock_get.return_value = mock_response
        
        url = "http://example.com/Test_Page"
        success = ingestor.scrape_url(url)
        
        assert success is True
        
        # Verify file creation
        expected_file = temp_data_dir / "Test_Page.txt"
        assert expected_file.exists()
        
        content = expected_file.read_text(encoding="utf-8")
        assert "Source URL: http://example.com/Test_Page" in content
        assert "Hello World" in content

    @patch('requests.get')
    def test_scrape_url_failure(self, mock_get, temp_data_dir):
        """Test handling of request errors."""
        ingestor = DataIngestor(str(temp_data_dir))
        
        mock_get.side_effect = requests.exceptions.ConnectionError("Boom")
        
        success = ingestor.scrape_url("http://bad-url.com")
        assert success is False
