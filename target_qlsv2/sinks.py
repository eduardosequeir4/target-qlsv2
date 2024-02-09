"""QlsV2 target sink class, which handles writing streams."""

import ast
from datetime import datetime

from target_qlsv2.client import QlsV2Sink


class BuyOrdersV2Sink(QlsV2Sink):
    """QlsV2 target sink class."""

    name = "BuyOrders"
    endpoint = "purchase-orders"

    def preprocess_record(self, record: dict, context: dict) -> dict:
        dateoriginal = datetime.strptime(record["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        dateoriginal = dateoriginal.strftime("%Y-%m-%d")
        deliveries= [{"estimated_arrival":dateoriginal}]
        if "line_items" in record:
            record["line_items"] = ast.literal_eval(record["line_items"])
            purchase_order_products = list(
                map(
                    lambda product: {
                        "remoteId": product["remoteId"],
                        "product_payload": {
                            "amount": product["quantity"],
                            "fulfillment_product_id": product["product_remoteId"],
                        },
                    },
                    list(record["line_items"]),
                )
            )

            payload = {"suppliers": [record["supplier_remoteId"]], "customer_title": record["id"],"pre_order": 0,"purchase_order_products": purchase_order_products, "deliveries": deliveries}

            processed_record = {
                "buy_order_remoteId": record["remoteId"],
                "payload": payload,
            }

        else:
            processed_record = None

        return processed_record

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record."""
        if record:
            try:
                if record["buy_order_remoteId"]:
                    remoteId = record["buy_order_remoteId"]
                    qlsv2_buy_order = self.request_api(
                        "GET", endpoint=f"{self.endpoint}/{remoteId}"
                    )
                    buy_order_json = qlsv2_buy_order.json()

                    if buy_order_json["data"]:
                        for product in record["payload"]["purchase_order_products"]:
                            if not product["remoteId"]:
                                response = self.request_api(
                                    "POST",
                                    endpoint=f"{self.endpoint}/{remoteId}/purchase-order-products",
                                    request_data=product["product_payload"],
                                )
                                id = response.json()["data"]["id"]
                                self.logger.info(f"order line added with id: {id}")

                else:
                    endpoint = f"{self.endpoint}"
                    new_lines = list(
                                    map(
                                        lambda product: {
                                            "amount": product["product_payload"]["amount"],
                                            "fulfillment_product_id": product["product_payload"]["fulfillment_product_id"]
                                        },
                                        list(record["payload"]["purchase_order_products"]),
                                    )
                                )
                    record["payload"]["purchase_order_products"] = new_lines
                    response = self.request_api(
                        "POST", endpoint=endpoint, request_data=record["payload"]
                    )
                    id = response.json()["data"]["id"]
                    self.logger.info(f"{self.name} created with id: {id}")
            except:
                raise KeyError

class UpdateInventorySink(QlsV2Sink):
    """QlsV2 target sink class."""
    name = "UpdateInventory"

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record."""
        return
