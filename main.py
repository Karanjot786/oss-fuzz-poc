#!/usr/bin/env python3
"""Main entry point for OSS-Fuzz coverage analysis tool."""

import argparse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from oss_fuzz_analysis import main

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze coverage and crash data for OSS-Fuzz projects"
    )
    parser.add_argument(
        "projects",
        nargs="+",
        help="List of OSS-Fuzz project names to analyze"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.projects)
