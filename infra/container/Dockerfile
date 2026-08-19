# Dockerfile for ADTC 2026 Simulation Container
# Base: Ubuntu 22.04 LTS (x86_64 / linux/amd64) matching adtc_standard_laptop.yml
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH="/usr/local/bin:/opt/adtc/bin:${PATH}"

# Install core build dependencies and runtime tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-dev \
    libgomp1 \
    ca-certificates \
    curl \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/adtc

# Build pinned llama.cpp from source (commit 0329fcdac8c2477c2dda1d5e43fd2e3616b99655)
RUN git clone https://github.com/ggml-org/llama.cpp.git /opt/adtc/llama.cpp \
    && cd /opt/adtc/llama.cpp \
    && git checkout 0329fcdac8c2477c2dda1d5e43fd2e3616b99655 \
    && cmake -B build -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON \
    && cmake --build build --config Release -j4 \
    && cp build/bin/llama-* /usr/local/bin/ || true \
    && cp build/bin/llama-cli /usr/local/bin/ \
    && cp build/bin/llama-bench /usr/local/bin/ \
    && cp build/bin/llama-quantize /usr/local/bin/ || true

# Install pinned adtc-profiler (commit ac2e137dca65ea3b09d997774f17dd8907b489fb)
RUN git clone https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git /opt/adtc/adtc-profiler \
    && cd /opt/adtc/adtc-profiler \
    && git checkout ac2e137dca65ea3b09d997774f17dd8907b489fb \
    && pip3 install --no-cache-dir .

# Create non-root runner user and directories
RUN useradd -m -u 1000 adtc-runner \
    && mkdir -p /submission /artifacts /tmp \
    && chown -R adtc-runner:adtc-runner /opt/adtc /artifacts /tmp

USER adtc-runner
WORKDIR /artifacts

ENTRYPOINT ["adtc-profiler"]
CMD ["--help"]
