# ---------------------------------------------------------------
# Image for the aSTEP map matching CLI (package "mapmatching")
#
#   docker build -t astep/mapmatching .
#   docker run --rm astep/mapmatching --help
#
# To pull the latest FMM master (the clone step is cached otherwise):
#   docker build --no-cache-filter fmm-build -t astep/mapmatching .
# ---------------------------------------------------------------

# ---------- Stage 1: build FMM (latest master) from source ----------
FROM python:3.12-slim-bookworm AS fmm-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake swig git \
        libgdal-dev libboost-dev libboost-serialization-dev \
        libexpat1-dev libbz2-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir setuptools

RUN git clone --depth 1 --branch master https://github.com/cyang-kth/fmm.git /src/fmm \
    && sed -i -e 's/c++11/c++14/g' \
              -e 's/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 14/' /src/fmm/CMakeLists.txt
WORKDIR /src/fmm/build
RUN cmake .. && make -j4 && make install

# ---------- Stage 2: the mapmatching image ----------
FROM python:3.12-slim-bookworm

# - no .pyc files, logs are printed immediately (important for `docker logs`)
# - no pip cache / version check, keeps the image small and the build quiet
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# FMM: runtime libraries only (no compilers), then copy the compiled programs
# and Python bindings from the build stage. Must come before any pip install,
# because it replaces /usr/local (where Python and its packages live).
RUN apt-get update && apt-get install -y --no-install-recommends \
        gdal-bin libgdal32 libboost-serialization1.74.0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=fmm-build /usr/local /usr/local

# Fail the build early if a runtime library or the Python module is missing
RUN ! ldd /usr/local/bin/fmm | grep "not found" \
    && python -c "import fmm"

WORKDIR /app

# 1) Dependencies only.
#    The list is read straight from pyproject.toml, so there is only one place
#    to add a dependency. This layer is cached and only re-runs when
#    pyproject.toml changes - not every time the code changes.
#    psycopg[binary] ships its own libpq, so no extra apt packages are needed here.
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