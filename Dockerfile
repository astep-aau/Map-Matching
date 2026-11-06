# ---------------------------------------------------------------
# Image for the aSTEP map matching CLI (package "mapmatching")
#
#   docker build -t astep/mapmatching .
#   docker run --rm astep/mapmatching --help
# ---------------------------------------------------------------
FROM python:3.12-slim

# - no .pyc files, logs are printed immediately (important for `docker logs`)
# - no pip cache / version check, keeps the image small and the build quiet
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1) Dependencies only.
#    The list is read straight from pyproject.toml, so there is only one place
#    to add a dependency. This layer is cached and only re-runs when
#    pyproject.toml changes - not every time the code changes.
#    No apt packages are needed: psycopg[binary] ships its own libpq.
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']))" > /tmp/requirements.txt \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# 2) The package itself (README.md is required by pyproject's `readme` field)
COPY README.md ./
COPY src ./src
RUN pip install --no-deps .

# Do not run as root inside the container
RUN useradd --create-home --uid 1000 mapmatch
USER mapmatch

# The image behaves like the `mapmatch` command:
#   docker run --rm astep/mapmatching repotest
ENTRYPOINT ["mapmatch"]
CMD ["--help"]
