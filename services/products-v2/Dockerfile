FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY products_v2/ products_v2/
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY products_v2/ products_v2/

USER appuser
EXPOSE 8000

CMD ["uvicorn", "products_v2.main:app", "--host", "0.0.0.0", "--port", "8000"]
