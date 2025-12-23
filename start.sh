#!/bin/bash
echo "🌍 Starting EU5 Oracle..."
echo "ℹ️  Ensure you have run 'python src/ingestion.py' at least once if this is a fresh install."
streamlit run src/ui.py
