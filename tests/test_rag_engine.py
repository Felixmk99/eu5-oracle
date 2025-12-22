import pytest
from unittest.mock import MagicMock, patch
from rag_engine import RAGEngine

class TestRAGEngine:
    
    @pytest.fixture
    def mock_chroma(self):
        with patch('rag_engine.chromadb.PersistentClient') as mock:
            yield mock

    @patch('rag_engine.SimpleDirectoryReader')
    @patch('rag_engine.VectorStoreIndex')
    @patch('rag_engine.ChromaVectorStore')
    @patch('rag_engine.StorageContext')
    def test_build_index_slow_path(self, mock_storage_ctx, mock_cvs, mock_vsi, mock_sdr, mock_chroma, temp_data_dir, temp_chroma_dir):
        """Test building index when DB is empty (Slow Path)."""
        
        # Setup mocks
        mock_db_client = mock_chroma.return_value
        mock_collection = mock_db_client.get_or_create_collection.return_value
        mock_collection.count.return_value = 0 # Empty DB
        
        # Create a dummy file so glob finds it
        (temp_data_dir / "test.txt").write_text("content")
        
        engine = RAGEngine(str(temp_data_dir), str(temp_chroma_dir))
        index = engine.load_index()
        
        # Assertions
        # 1. verify SimpleDirectoryReader was called since DB count was 0
        mock_sdr.assert_called()
        
        # 2. verify we tried to list files (glob/iterdir logic is internal but we verify result of SDR loading)
        mock_sdr.return_value.load_data.assert_called_once()
        
        # 3. verify Index created from documents
        mock_vsi.from_documents.assert_called_once()
        mock_vsi.from_vector_store.assert_not_called()

    @patch('rag_engine.SimpleDirectoryReader')
    @patch('rag_engine.VectorStoreIndex')
    @patch('rag_engine.ChromaVectorStore')
    @patch('rag_engine.StorageContext')
    def test_load_index_fast_path(self, mock_storage_ctx, mock_cvs, mock_vsi, mock_sdr, mock_chroma, temp_data_dir, temp_chroma_dir):
        """Test loading index when DB has data (Fast Path)."""
        
        # Setup mocks
        mock_db_client = mock_chroma.return_value
        mock_collection = mock_db_client.get_or_create_collection.return_value
        mock_collection.count.return_value = 100 # Data exists
        
        engine = RAGEngine(str(temp_data_dir), str(temp_chroma_dir))
        index = engine.load_index()
        
        # Assertions
        # 1. SimpleDirectoryReader should NOT be called
        mock_sdr.assert_not_called()
        
        # 2. Index loaded from vector store
        mock_vsi.from_vector_store.assert_called_once()
        mock_vsi.from_documents.assert_not_called()
