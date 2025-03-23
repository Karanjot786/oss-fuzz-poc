import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import os

def fetch_project_metadata(project_names):
    """Fetch project metadata from GitHub API.

    Args:
        project_names (list): List of project names to fetch metadata for.

    Returns:
        dict: A dictionary where:
            - keys are project names (str)
            - values are either project metadata (dict) from GitHub API
              or error message (dict) if project not found

    Raises:
        requests.RequestException: If there's an error connecting to GitHub API

    Example:
        >>> metadata = fetch_project_metadata(["zlib"])
        >>> print(metadata["zlib"])
        {'name': 'zlib', 'path': 'projects/zlib', ...}
    """
    metadata = {}
    for project in project_names:
        url = f"https://api.github.com/repos/google/oss-fuzz/contents/projects/{project}"
        response = requests.get(url)
        if response.status_code == 200:
            metadata[project] = response.json()
        else:
            metadata[project] = {"error": "Project not found"}
    return metadata

def fetch_project_data(project_names):
    """Fetch simulated project data for crashes and coverage.

    Args:
        project_names (list): List of project names to fetch data for.

    Returns:
        dict: A dictionary where:
            - keys are project names (str)
            - values are dictionaries containing:
                - crashes (pd.DataFrame): Crash data with columns:
                    - date (str): Date of crash
                    - crash_hash (str): Unique crash identifier
                    - type (str): Type of crash
                - coverage (pd.DataFrame): Coverage data with columns:
                    - date (str): Date of coverage measurement
                    - coverage (float): Coverage percentage

    Note:
        Currently uses simulated data. In production, this would fetch
        real data from OSS-Fuzz's crash and coverage databases.
    """
    project_data = {}
    coverage_base = {
        "zlib": 70,
        "libpng": 75,
        "openssl": 65
    }
    
    for project in project_names:
        crash_data = [
            {"date": "15-01-2025", "crash_hash": "mno345", "type": "null-pointer"},  
            {"date": "28-01-2025", "crash_hash": "pqr678", "type": "division-by-zero"},  
            {"date": "31-01-2025", "crash_hash": "jkl012", "type": "integer-overflow"},   
            {"date": "10-02-2025", "crash_hash": "stu901", "type": "buffer-overflow"},  
            {"date": "20-02-2025", "crash_hash": "vwx234", "type": "race-condition"}, 
            {"date": "25-02-2025", "crash_hash": "ghi789", "type": "stack-overflow"},
            {"date": "06-03-2025", "crash_hash": "def456", "type": "use-after-free"},
            {"date": "06-03-2025", "crash_hash": "abc123", "type": "heap-overflow"},
            {"date": "15-03-2025", "crash_hash": "abc123", "type": "heap-overflow"}
        ]
        
        # Generate different coverage data for each project
        base = coverage_base[project]
        coverage_data = [
            {"date": "15-01-2025", "coverage": base},
            {"date": "28-01-2025", "coverage": base + 3},
            {"date": "31-01-2025", "coverage": base + 5},
            {"date": "10-02-2025", "coverage": base + 7},
            {"date": "20-02-2025", "coverage": base + 10},
            {"date": "25-02-2025", "coverage": base + 12},
            {"date": "06-03-2025", "coverage": base + 15},
            {"date": "06-03-2025", "coverage": base + 17},
            {"date": "15-03-2025", "coverage": base + 20}
        ]
        
        project_data[project] = {
            "crashes": pd.DataFrame(crash_data),
            "coverage": pd.DataFrame(coverage_data)
        }
    return project_data

def analyze_project_data(project_data):
    """Analyze project data for unique crashes and coverage trends.

    Args:
        project_data (dict): Dictionary containing crash and coverage data for each project.
            Expected format:
            {
                'project_name': {
                    'crashes': pd.DataFrame,
                    'coverage': pd.DataFrame
                }
            }

    Returns:
        dict: Analysis results where:
            - keys are project names (str)
            - values are dictionaries containing:
                - unique_crashes (int): Number of unique crash hashes
                - avg_coverage (float): Average coverage percentage
                - coverage_trend (list): Coverage data points over time

    Note:
        Growth rate calculations use pandas' pct_change method,
        which calculates percentage change between consecutive values.
    """
    analysis = {}
    for project, data in project_data.items():
        unique_crashes = data["crashes"]["crash_hash"].nunique()
        coverage_df = data["coverage"]
        avg_coverage = coverage_df["coverage"].mean()
        coverage_df["growth_rate"] = coverage_df["coverage"].pct_change() * 100
        coverage_df["date"] = coverage_df["date"].astype(str)
        analysis[project] = {
            "unique_crashes": int(unique_crashes),
            "avg_coverage": float(avg_coverage),
            "coverage_trend": coverage_df.to_dict(orient="records")
        }
    return analysis

def plot_coverage_trends(project_data, project_names):
    """Plot coverage trends for each project.

    Args:
        project_data (dict): Dictionary containing coverage DataFrames for each project.
            Expected format same as analyze_project_data input.
        project_names (list): List of project names to plot.

    Returns:
        None: Saves the plot to 'coverage_trends.png'

    Note:
        - Uses matplotlib to create a line plot with markers
        - Each project gets a different color automatically
        - Dates are automatically formatted on x-axis
        - Plot is saved and closed to free memory
    """
    plt.figure(figsize=(10, 6))
    for project in project_names:
        df = project_data[project]["coverage"].copy()  # Create a copy to avoid modifying original
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        # Sort by date to ensure proper trend lines
        df = df.sort_values("date")
        # Set index and plot in one operation
        plt.plot(df["date"], df["coverage"], marker='o', linestyle='-', label=project)
    
    plt.title("Coverage Trends Across Projects")
    plt.xlabel("Date")
    plt.ylabel("Coverage (%)")
    plt.legend()
    plt.grid(True)
    output_path = os.path.join(os.path.dirname(__file__), "../../outputs/coverage_trends.png")
    plt.savefig(output_path)
    plt.close()  # Close the plot to free memory

def main(project_names):
    """Run the data fetching, analysis, and plotting pipeline.

    Args:
        project_names (list): List of project names to process.

    Returns:
        None: Writes results to 'oss_fuzz_analysis.json' and creates plot

    Raises:
        JSONDecodeError: If there's an error writing the JSON file
        IOError: If there's an error saving the plot file

    Note:
        The output JSON file contains three main sections:
        - metadata: Project information from GitHub
        - analysis: Statistical analysis of crashes and coverage
        - raw_data: Original crash and coverage data
    """
    metadata = fetch_project_metadata(project_names)
    project_data = fetch_project_data(project_names)
    analysis = analyze_project_data(project_data)
    plot_coverage_trends(project_data, project_names)
    
    # Create a modified version of raw_data that properly handles date formatting
    raw_data = {}
    for p, d in project_data.items():
        crashes_df = d["crashes"].copy()
        coverage_df = d["coverage"].copy()
        
        # Simply use the string dates as they already are
        raw_data[p] = {
            "crashes": crashes_df.to_dict(orient="records"),
            "coverage": coverage_df.to_dict(orient="records")
        }
    
    results = {
        "metadata": metadata,
        "analysis": analysis,
        "raw_data": raw_data
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "../../outputs/oss_fuzz_analysis.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    projects = ["zlib", "libpng", "openssl"]
    main(projects)