import pytest
import numpy as np
from unittest.mock import Mock, patch

from app.services.llm_client import MockLLMClient, TinyLlamaClient, OpenAIClient, get_llm_client


@pytest.mark.unit
class TestMockLLMClient:
    """Test MockLLMClient functionality."""
    
    def test_generate_embedding(self):
        """Test embedding generation."""
        client = MockLLMClient()
        text = "This is a test text for embedding generation."
        
        embedding = client.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
        assert -1 <= min(embedding) and max(embedding) <= 1
    
    def test_extract_kpis(self):
        """Test KPI extraction."""
        client = MockLLMClient()
        text = "Carbon emissions: 1250.5 tons CO2e. Energy consumption: 2500 MWh."
        
        kpis = client.extract_kpis(text)
        
        assert isinstance(kpis, list)
        assert len(kpis) >= 1
        
        # Check structure of extracted KPIs
        for kpi in kpis:
            assert "name" in kpi
            assert "value" in kpi
            assert "unit" in kpi
            assert "confidence" in kpi
    
    def test_generate_guidance(self):
        """Test guidance generation."""
        client = MockLLMClient()
        context = {
            "organization": "Test Corp",
            "kpi": "Carbon Emissions",
            "current_value": 1250.5,
            "benchmark": 1000.0
        }
        
        guidance = client.generate_guidance(context)
        
        assert isinstance(guidance, dict)
        assert "recommendations" in guidance
        assert "action_items" in guidance
        assert "priority" in guidance
        assert isinstance(guidance["recommendations"], list)
        assert isinstance(guidance["action_items"], list)


@pytest.mark.unit
class TestTinyLlamaClient:
    """Test TinyLlamaClient functionality."""
    
    @patch('app.services.llm_client.AutoTokenizer')
    @patch('app.services.llm_client.AutoModel')
    def test_initialization(self, mock_model, mock_tokenizer):
        """Test TinyLlama client initialization."""
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        client = TinyLlamaClient(model_path="test/path")
        
        assert client.model_path == "test/path"
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()
    
    @patch('app.services.llm_client.AutoTokenizer')
    @patch('app.services.llm_client.AutoModel')
    def test_generate_embedding_with_mock(self, mock_model, mock_tokenizer):
        """Test embedding generation with mocked model."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {
            'input_ids': [[1, 2, 3]],
            'attention_mask': [[1, 1, 1]]
        }
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_output = Mock()
        mock_output.last_hidden_state = np.random.rand(1, 3, 768)
        mock_model_instance.return_value = mock_output
        mock_model.from_pretrained.return_value = mock_model_instance
        
        client = TinyLlamaClient(model_path="test/path")
        embedding = client.generate_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 768  # Hidden size


@pytest.mark.unit
class TestOpenAIClient:
    """Test OpenAIClient functionality."""
    
    @patch('app.services.llm_client.openai.Embedding.create')
    def test_generate_embedding(self, mock_create):
        """Test OpenAI embedding generation."""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=list(np.random.rand(1536)))]
        mock_create.return_value = mock_response
        
        client = OpenAIClient(api_key="test-key")
        embedding = client.generate_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        mock_create.assert_called_once()
    
    @patch('app.services.llm_client.openai.ChatCompletion.create')
    def test_extract_kpis(self, mock_create):
        """Test OpenAI KPI extraction."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='[{"name": "Carbon Emissions", "value": 1250.5, "unit": "tons CO2e", "confidence": 0.9}]'))]
        mock_create.return_value = mock_response
        
        client = OpenAIClient(api_key="test-key")
        kpis = client.extract_kpis("Carbon emissions: 1250.5 tons CO2e")
        
        assert isinstance(kpis, list)
        assert len(kpis) == 1
        assert kpis[0]["name"] == "Carbon Emissions"
        assert kpis[0]["value"] == 1250.5


@pytest.mark.unit
class TestLLMClientFactory:
    """Test LLM client factory function."""
    
    def test_get_mock_client(self):
        """Test getting mock client."""
        with patch('app.services.llm_client.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "mock"
            
            client = get_llm_client()
            
            assert isinstance(client, MockLLMClient)
    
    def test_get_openai_client(self):
        """Test getting OpenAI client."""
        with patch('app.services.llm_client.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "openai"
            mock_settings.return_value.openai_api_key = "test-key"
            
            client = get_llm_client()
            
            assert isinstance(client, OpenAIClient)
    
    def test_get_tinyllama_client(self):
        """Test getting TinyLlama client."""
        with patch('app.services.llm_client.get_settings') as mock_settings, \
             patch('app.services.llm_client.AutoTokenizer'), \
             patch('app.services.llm_client.AutoModel'):
            
            mock_settings.return_value.llm_provider = "tinyllama"
            mock_settings.return_value.tinyllama_model_path = "test/path"
            
            client = get_llm_client()
            
            assert isinstance(client, TinyLlamaClient)
    
    def test_invalid_provider_fallback(self):
        """Test fallback to mock client for invalid provider."""
        with patch('app.services.llm_client.get_settings') as mock_settings:
            mock_settings.return_value.llm_provider = "invalid"
            
            client = get_llm_client()
            
            assert isinstance(client, MockLLMClient)
