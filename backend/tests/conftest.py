"""
Global pytest configuration for NEXUS-RAG.
Ensures backend package is on sys.path across all CI runners and local environments.
"""
import sys
from pathlib import Path

# Resolve root and backend paths
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent  # backend/

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
