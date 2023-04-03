import os
from sp_api.api import Orders
from sp_api.base import SellingApiException, Marketplaces


def get_amazon_sales(start_date, end_date, marketplace_id):
    try:
        orders_api = Orders(
            account="default",
            credentials=dict(
                refresh_token=os.getenv("AMAZON_REFRESH_TOKEN"),
                lwa_app_id=os.getenv("AMAZON_APP_ID"),
                lwa_client_secret=os.getenv("AMAZON_CLIENT_SECRET"),
                aws_secret_key=os.getenv("AMAZON_SECRET_KEY"),
                aws_access_key=os.getenv("AMAZON_ACCESS_KEY"),
                role_arn=os.getenv("AMAZON_ROLE_ARN"),
            ),
        )

        sales_data = orders_api.get_orders(
            CreatedAfter=start_date,
            CreatedBefore=end_date,
            MarketplaceIds=[marketplace_id],
        )

        return sales_data.payload["Orders"]
    except SellingApiException as ex:
        print(f"Error: {ex}")
        return None
