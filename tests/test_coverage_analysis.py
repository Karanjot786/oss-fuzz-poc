import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import json
from unittest.mock import patch, Mock
import os

from oss_fuzz_analysis import (
    fetch_project_metadata,
    fetch_project_data,
    analyze_project_data,
    plot_coverage_trends,
)
@pytest.fixture
def mock_github_response():
    """Mock GitHub API response."""
    return {
        "name": "test_project",
        "path": "projects/test_project",
        "type": "dir"
    }

@pytest.fixture
def sample_project_data():
    """Create sample project data for testing."""
    crash_data = pd.DataFrame([
        {"date": "15-01-2025", "crash_hash": "test123", "type": "null-pointer"}
    ])
    coverage_data = pd.DataFrame([
        {"date": "15-01-2025", "coverage": 75.0}
    ])
    return {
        "test_project": {
            "crashes": crash_data,
            "coverage": coverage_data
        }
    }

@pytest.fixture
def output_files():
    """Handle test output files."""
    yield
    # Cleanup after tests
    output_dir = os.path.join(os.path.dirname(__file__), "../outputs")
    files_to_clean = [
        os.path.join(output_dir, 'coverage_trends.png'),
        os.path.join(output_dir, 'oss_fuzz_analysis.json')
    ]
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)

def test_fetch_project_metadata():
    """Test project metadata fetching."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"name": "test_project"}
        
        result = fetch_project_metadata(["test_project"])
        assert "test_project" in result
        assert result["test_project"]["name"] == "test_project"

def test_fetch_project_data():
    """Test project data generation."""
    result = fetch_project_data(["zlib"])
    assert "zlib" in result
    assert "crashes" in result["zlib"]
    assert "coverage" in result["zlib"]
    assert isinstance(result["zlib"]["crashes"], pd.DataFrame)
    assert isinstance(result["zlib"]["coverage"], pd.DataFrame)

def test_analyze_project_data(sample_project_data):
    """Test data analysis functionality."""
    result = analyze_project_data(sample_project_data)
    assert "test_project" in result
    assert "unique_crashes" in result["test_project"]
    assert "avg_coverage" in result["test_project"]
    assert "coverage_trend" in result["test_project"]

def test_plot_coverage_trends(sample_project_data, output_files):
    """Test plot generation."""
    plot_coverage_trends(sample_project_data, ["test_project"])
    assert os.path.exists("coverage_trends.png")

def test_invalid_project_metadata():
    """Test handling of invalid projects."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        result = fetch_project_metadata(["invalid_project"])
        assert "invalid_project" in result
        assert result["invalid_project"]["error"] == "Project not found"

def test_coverage_data_format():
    """Test coverage data format and calculations."""
    result = fetch_project_data(["zlib"])
    coverage_df = result["zlib"]["coverage"]
    
    assert "date" in coverage_df.columns
    assert "coverage" in coverage_df.columns
    assert coverage_df["coverage"].dtype in [float, int]
    assert coverage_df["date"].dtype == object
