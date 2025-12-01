# ============================================================================
# MASTERMIND FIX 2025 — BACKEND DOCKERFILE (ZERO COMPILE)
# ============================================================================
# Uses pre-built base image + binary wheels only
# Build time: <15 seconds with cache
# ============================================================================

FROM ghcr.io/cliffcho242/hiremebahamas-base-backend:latest

COPY requirements.txt .

# MASTERMIND FIX 2025 — NUCLEAR BINARY-ONLY INSTALL
RUN pip install --upgrade pip && \
    pip install --only-binary=:all: -r requirements.txt

COPY . .

RUN mkdir -p uploads/avatars uploads/portfolio uploads/documents

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c 'curl -f http://localhost:${PORT:-8000}/health || exit 1'

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]