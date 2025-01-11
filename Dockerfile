FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1 \
    PATH="$PATH:/root/.local/bin"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /bot

# Copy project files
COPY pyproject.toml ./

# Install Python dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application source code
COPY ./bot ./bot

# Define default command
CMD ["poetry", "run", "python", "-m", "bot.main"]