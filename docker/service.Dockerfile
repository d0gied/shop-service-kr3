FROM ghcr.io/astral-sh/uv:python3.13-alpine


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/service/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=from=packages,target=/app/packages \
    uv sync --locked --no-install-project --no-install-workspace

# Copy the project into the image
ADD . /app/service/app

COPY --from=packages common /app/packages/common

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked