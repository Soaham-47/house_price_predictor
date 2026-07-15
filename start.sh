#!/bin/bash

# Start the FastAPI service via Uvicorn in the background using 'uv'
# Make sure the module path matches where your app initialization lives inside src/
uv run uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &

# Wait briefly for the API to boot up completely
sleep 3

# Launch the primary interface via Streamlit on the mandatory HF port
uv run streamlit run app.py --server.port 7860 --server.address 0.0.0.0