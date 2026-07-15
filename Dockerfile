FROM python:3.11-slim

WORKDIR /workspace

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv directly
RUN pip install uv

# Copy the lockfiles first to optimize Docker layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies explicitly without creating a virtualenv wrapper inside the container
RUN uv sync --frozen --no-install-project

# Copy the remaining project directories and files visible in your tree
COPY . .

# Explicitly ensure the project package itself is synced
RUN uv sync --frozen

# Configure local networking variable for app.py
ENV API_URL=http://127.0.0.1:8000

# Grant executable permission to the script
RUN chmod +x start.sh

# Expose the mandatory Hugging Face frontend port
EXPOSE 7860

CMD ["./start.sh"]