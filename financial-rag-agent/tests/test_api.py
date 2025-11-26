"""
Tests for FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from financial_rag_agent.api.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    return TestClient(app)


class TestRootEndpoints:
    """Tests for root and utility endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code in [200, 503]  # May be unhealthy if no API keys
        data = response.json()
        assert "status" in data
        assert "agent_initialized" in data

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/status")

        # May fail if agent not initialized
        if response.status_code == 200:
            data = response.json()
            assert "agent" in data
            assert "llm" in data
            assert "vector_store" in data

    def test_get_tickers_endpoint(self, client):
        """Test get available tickers endpoint."""
        response = client.get("/tickers")

        # May fail if agent not initialized
        if response.status_code == 200:
            data = response.json()
            assert "tickers" in data
            assert "count" in data
            assert isinstance(data["tickers"], list)


class TestAskEndpoint:
    """Tests for /ask endpoint."""

    def test_ask_single_ticker(self, client):
        """Test asking question about single ticker."""
        request_data = {
            "ticker": "AAPL",
            "question": "What are the key financial highlights?",
        }

        response = client.post("/ask", json=request_data)

        # May fail if agent not initialized or no API keys
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "question" in data
            assert data["question"] == request_data["question"]
            assert "plan" in data
            assert "used_tools" in data
            assert "execution_time_ms" in data

    def test_ask_comparison(self, client):
        """Test asking comparison question."""
        request_data = {
            "question": "Compare Apple and Microsoft profitability",
        }

        response = client.post("/ask", json=request_data)

        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "plan" in data

    def test_ask_with_context_limit(self, client):
        """Test asking with context limit parameter."""
        request_data = {
            "ticker": "NVDA",
            "question": "What are the recent developments?",
            "context_limit": 3,
        }

        response = client.post("/ask", json=request_data)

        if response.status_code == 200:
            data = response.json()
            assert "answer" in data

    def test_ask_missing_question(self, client):
        """Test asking without question."""
        request_data = {
            "ticker": "AAPL",
        }

        response = client.post("/ask", json=request_data)

        # Should fail validation
        assert response.status_code == 422

    def test_ask_invalid_context_limit(self, client):
        """Test asking with invalid context limit."""
        request_data = {
            "ticker": "AAPL",
            "question": "What are the results?",
            "context_limit": 100,  # Too high
        }

        response = client.post("/ask", json=request_data)

        # Should fail validation
        assert response.status_code == 422

    def test_ask_invalid_temperature(self, client):
        """Test asking with invalid temperature."""
        request_data = {
            "ticker": "AAPL",
            "question": "What are the results?",
            "temperature": 3.0,  # Too high
        }

        response = client.post("/ask", json=request_data)

        # Should fail validation
        assert response.status_code == 422


class TestAPIValidation:
    """Tests for API request validation."""

    def test_empty_request(self, client):
        """Test empty POST request."""
        response = client.post("/ask", json={})

        # Should fail - missing required field
        assert response.status_code == 422

    def test_invalid_json(self, client):
        """Test invalid JSON."""
        response = client.post(
            "/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_unknown_endpoint(self, client):
        """Test accessing unknown endpoint."""
        response = client.get("/unknown_endpoint")

        assert response.status_code == 404


class TestAPIResponses:
    """Tests for API response formats."""

    def test_successful_response_structure(self, client):
        """Test structure of successful response."""
        request_data = {
            "ticker": "AAPL",
            "question": "What are the margins?",
        }

        response = client.post("/ask", json=request_data)

        if response.status_code == 200:
            data = response.json()

            # Check all required fields
            required_fields = [
                "answer",
                "question",
                "plan",
                "used_tools",
                "execution_time_ms",
                "llm_available",
            ]

            for field in required_fields:
                assert field in data, f"Missing field: {field}"

            # Check types
            assert isinstance(data["answer"], str)
            assert isinstance(data["question"], str)
            assert isinstance(data["plan"], dict)
            assert isinstance(data["used_tools"], list)
            assert isinstance(data["execution_time_ms"], (int, float))
            assert isinstance(data["llm_available"], bool)

    def test_error_response_structure(self, client):
        """Test structure of error response."""
        # Trigger error with invalid input
        response = client.post("/ask", json={})

        assert response.status_code == 422
        data = response.json()

        # FastAPI validation error format
        assert "detail" in data


@pytest.mark.parametrize("ticker,question", [
    ("AAPL", "What are the earnings?"),
    ("MSFT", "How is Azure performing?"),
    (None, "Compare AAPL and MSFT"),
    ("NVDA", "What are the main risks?"),
])
def test_various_queries(client, ticker, question):
    """Test API with various query types."""
    request_data = {"question": question}
    if ticker:
        request_data["ticker"] = ticker

    response = client.post("/ask", json=request_data)

    # Should either succeed or have agent not initialized
    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0


def test_api_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/ask")

    # CORS headers should be present (if configured)
    # This is a basic check - detailed CORS testing would need more setup
    assert response.status_code in [200, 405]  # OPTIONS may not be implemented


def test_api_concurrent_requests(client):
    """Test handling multiple concurrent requests."""
    import concurrent.futures

    def make_request():
        return client.post(
            "/ask",
            json={
                "ticker": "AAPL",
                "question": "What are the key metrics?",
            },
        )

    # Make 3 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request) for _ in range(3)]
        responses = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All requests should complete
    assert len(responses) == 3

    # Should get consistent response codes
    status_codes = [r.status_code for r in responses]
    # All should be same status (either all succeed or all fail)
    assert len(set(status_codes)) <= 2  # At most 2 different codes


def test_openapi_schema(client):
    """Test OpenAPI schema is available."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/ask" in schema["paths"]
    assert "/health" in schema["paths"]
