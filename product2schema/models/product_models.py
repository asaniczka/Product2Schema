from typing import List, Optional
from datetime import datetime
import json

from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    product_id: str | None = Field(
        None, description="A unique identifier for the product"
    )
    product_name: str = Field(..., description="The name of the product")
    currency_symbol: str | None = Field(
        None, description="Currency Symbol of the price"
    )
    base_price: float | None = Field(
        None, description="The regular price of the product"
    )
    buy_now_price: float | None = Field(
        None, description="The price for buying the product instantly"
    )
    full_description: str | None = Field(
        None, description="Full description of the product"
    )
    product_rating: float | None = Field(
        None, description="Rating of the product given by users"
    )
    product_review_count: int | None = Field(
        None, description="Number of users who have left reviews"
    )
    brand_name: str | None = Field(None, description="Name of the brand")
    available_stock: int | None = Field(
        None, description="The number of items in stock as INT"
    )
    categories: list[str] | None = Field(
        None, description="The category to which the product belongs"
    )
    variants: list[str] | None = Field(
        None, description="Different variations of the product if available"
    )
    date_added: datetime | None = Field(
        None, description="The date and time the product was added to the catalog"
    )


class ProductSchema(BaseModel):
    is_product_page: bool
    product_metadata: Product | None = None


main_model_schema = ProductSchema.model_json_schema()
OPENAPI_SCHEMA = json.dumps(main_model_schema, indent=2)
