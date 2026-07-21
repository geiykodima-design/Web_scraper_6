from dataclasses import dataclass, fields, astuple


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int
    additional_info: dict

    def to_tuple(self):
        return astuple(self)

    @classmethod
    def get_field_names(cls):
        return [field.name for field in fields(cls)]


PRODUCT_FIELDS = [field.name for field in fields(Product)]