from typing import Any, Dict, List, Optional, Tuple

# Constants
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

COUPON_SAVE10 = "SAVE10"
COUPON_SAVE20 = "SAVE20"
COUPON_VIP = "VIP"

SAVE10_RATE = 0.10
SAVE20_RATE_HIGH = 0.20
SAVE20_RATE_LOW = 0.05
SAVE20_THRESHOLD = 200

VIP_DISCOUNT_HIGH = 50
VIP_DISCOUNT_LOW = 10
VIP_THRESHOLD = 100


def parse_request(request: dict) -> Tuple[Any, Any, Any, Any]:
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def process_checkout(request: dict) -> dict:
    # Parse
    user_id, items, coupon, currency = parse_request(request)

    # Validate & normalize
    currency = normalize_currency(currency)
    items_list = validate_request(user_id=user_id, items=items)

    # Calculate
    subtotal = calculate_subtotal(items_list)
    discount = calculate_discount(subtotal=subtotal, coupon=coupon)
    total_after_discount = max(subtotal - discount, 0)

    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    # Build response
    order_id = build_order_id(user_id=user_id, items_count=len(items_list))
    return build_response(
        order_id=order_id,
        user_id=user_id,
        currency=currency,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        items_count=len(items_list),
    )


def normalize_currency(currency: Optional[str]) -> str:
    return currency if currency is not None else DEFAULT_CURRENCY


def validate_request(*, user_id: Any, items: Any) -> List[Dict[str, Any]]:
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    validate_items(items)
    return items


def validate_items(items: List[Dict[str, Any]]) -> None:
    for it in items:
        if "price" not in it or "qty" not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items: List[Dict[str, Any]]) -> int:
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    return subtotal


def calculate_discount(*, subtotal: int, coupon: Optional[str]) -> int:
    if coupon is None or coupon == "":
        return 0

    if coupon == COUPON_SAVE10:
        return int(subtotal * SAVE10_RATE)

    if coupon == COUPON_SAVE20:
        rate = SAVE20_RATE_HIGH if subtotal >= SAVE20_THRESHOLD else SAVE20_RATE_LOW
        return int(subtotal * rate)

    if coupon == COUPON_VIP:
        return VIP_DISCOUNT_HIGH if subtotal >= VIP_THRESHOLD else VIP_DISCOUNT_LOW

    raise ValueError("unknown coupon")


def calculate_tax(amount: int) -> int:
    return int(amount * TAX_RATE)


def build_order_id(*, user_id: Any, items_count: int) -> str:
    return f"{user_id}-{items_count}-X"


def build_response(
    *,
    order_id: str,
    user_id: Any,
    currency: str,
    subtotal: int,
    discount: int,
    tax: int,
    total: int,
    items_count: int,
) -> dict:
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": items_count,
    }
