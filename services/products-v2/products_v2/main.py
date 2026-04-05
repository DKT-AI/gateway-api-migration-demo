import structlog
from fastapi import FastAPI, HTTPException

from products_v2.config import settings
from products_v2.data import get_all_products, get_product_by_id, get_recommendations

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
)

log: structlog.stdlib.BoundLogger = structlog.get_logger()

app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.service_name}


@app.get("/api/products")
async def list_products() -> list[dict[str, object]]:
    products = get_all_products()
    log.info("listing_products", count=len(products))
    return products  # type: ignore[return-value]


@app.get("/api/products/{product_id}")
async def get_product(product_id: int) -> dict[str, object]:
    product = get_product_by_id(product_id)
    if product is None:
        log.warning("product_not_found", product_id=product_id)
        raise HTTPException(status_code=404, detail="Product not found")
    log.info("getting_product", product_id=product_id)
    return product  # type: ignore[return-value]


@app.get("/api/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: int) -> list[dict[str, object]]:
    product = get_product_by_id(product_id)
    if product is None:
        log.warning("product_not_found", product_id=product_id)
        raise HTTPException(status_code=404, detail="Product not found")
    recs = get_recommendations(product_id)
    log.info("getting_recommendations", product_id=product_id, count=len(recs))
    return recs  # type: ignore[return-value]
