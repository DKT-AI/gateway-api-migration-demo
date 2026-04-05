FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY cart/ cart/
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY cart/ cart/

USER appuser
EXPOSE 8000

CMD ["uvicorn", "cart.main:app", "--host", "0.0.0.0", "--port", "8000"]
