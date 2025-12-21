#!/bin/bash

# Activate virtual environment and run dashboard
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run dashboard.py
