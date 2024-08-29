from http import HTTPMethod

from fastapi.routing import APIRoute

from app.api.web.controllers import index, carts, cart_items

routes = [
    APIRoute("/", methods=[HTTPMethod.GET], endpoint=index.index),
    APIRoute("/carts", methods=[HTTPMethod.POST], endpoint=carts.create),
    APIRoute("/carts/active", methods=[HTTPMethod.GET], endpoint=carts.retrieve_active),
    APIRoute(
        "/carts/{cart_id}/deactivate",
        methods=[HTTPMethod.POST],
        endpoint=carts.deactivate,
    ),
    APIRoute(
        "/carts/{cart_id}/apply-coupon",
        methods=[HTTPMethod.POST],
        endpoint=carts.apply_coupon,
    ),
    APIRoute(
        "/carts/{cart_id}/remove-coupon",
        methods=[HTTPMethod.POST],
        endpoint=carts.remove_coupon,
    ),
    APIRoute(
        "/carts/{cart_id}/items",
        methods=[HTTPMethod.POST],
        endpoint=cart_items.add_item,
    ),
    APIRoute(
        "/carts/{cart_id}/items/{item_id}",
        methods=[HTTPMethod.PATCH],
        endpoint=cart_items.update_item,
    ),
    APIRoute(
        "/carts/{cart_id}/items/{item_id}",
        methods=[HTTPMethod.DELETE],
        endpoint=cart_items.delete_item,
    ),
    APIRoute(
        "/carts/{cart_id}/items",
        methods=[HTTPMethod.DELETE],
        endpoint=cart_items.clear,
    ),
    # Mount(
    #     path="/static",
    #     app=StaticFiles(directory=Path(__file__).parent / "static"),
    #     name="static",
    # ),
]
