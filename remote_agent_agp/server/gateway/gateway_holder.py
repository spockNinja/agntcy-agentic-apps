"""Module gateway_holder: Contains the GatewayHolder class for managing the Gateway instance and FastAPI app."""

from typing import Optional

from agp_bindings import Gateway, GatewayConfig
from fastapi import FastAPI


class GatewayHolder:
    """
    A simple class to hold a reference to a Gateway instance.

    Attributes:
        gateway (Gateway): An instance of Gateway that this holder encapsulates.
            Defaults to None until a Gateway instance is assigned.
    """

    gateway: Gateway = None
    fastapi_app: Optional[FastAPI] = None

    @classmethod
    def get_fastapi_app(cls) -> FastAPI:
        """
        Returns the stored FastAPI application instance.
        """
        return cls.fastapi_app

    @classmethod
    def set_fastapi_app(cls, app: FastAPI) -> None:
        """
        Sets the FastAPI application instance.
        """
        cls.fastapi_app = app

    @classmethod
    def create_gateway(cls) -> Gateway:
        """
        Creates a new Gateway instance with the provided configuration.

        Args:
            config (GatewayConfig): The configuration for the Gateway.

        Returns:
            Gateway: The newly created Gateway instance.
        """
        cls.gateway = Gateway()
        return cls.gateway

    @classmethod
    def set_config(cls, endpoint, insecure) -> None:
        """
        Sets the Gateway instance.

        Args:
            config (Gateway): The configuration for the Gateway.
        """
        cls.gateway.config = GatewayConfig(endpoint=endpoint, insecure=insecure)
        cls.gateway.configure(cls.gateway.config)

    @classmethod
    def get_gateway(cls) -> Gateway:
        """
        Returns the stored Gateway instance.
        """
        return cls.gateway

    @classmethod
    def set_gateway(cls, gateway: Gateway) -> None:
        """
        Sets the Gateway instance.
        """
        cls.gateway = gateway

