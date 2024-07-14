"""Main models used by the engine"""

from pydantic import BaseModel

from product2schema.models.product_models import ProductSchema


class TransformUrlResponse(BaseModel):

    url: str
    cost: float | None = None
    product_schema: ProductSchema | None = None
