"""REST API MES Connector.

Generic connector for MES systems that expose REST APIs.
Supports configurable field mapping between MCP tools and MES endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from manugent.connector.base import MESConnectionConfig, MESConnector, QueryResult

logger = logging.getLogger(__name__)


# ============================================
# Default field mappings (can be overridden)
# ============================================

DEFAULT_ENDPOINT_MAP: dict[str, dict[str, Any]] = {
    "query_production_data": {
        "method": "GET",
        "path": "/production/metrics",
        "param_map": {
            "line_id": "line",
            "metric": "kpi",
            "time_range": "period",
            "granularity": "granularity",
        },
        "response_path": "data",
    },
    "query_wip": {
        "method": "GET",
        "path": "/production/wip",
        "param_map": {
            "line_id": "line",
            "product_id": "product",
            "station": "station",
        },
        "response_path": "data",
    },
    "query_production_orders": {
        "method": "GET",
        "path": "/production/orders",
        "param_map": {
            "order_id": "orderId",
            "status": "status",
            "time_range": "period",
        },
        "response_path": "data",
    },
    "get_equipment_status": {
        "method": "GET",
        "path": "/equipment/{equipment_id}/status",
        "param_map": {
            "equipment_id": "equipment_id",
        },
        "response_path": "data",
    },
    "get_equipment_history": {
        "method": "GET",
        "path": "/equipment/{equipment_id}/history",
        "param_map": {
            "equipment_id": "equipment_id",
            "days": "days",
        },
        "response_path": "data",
    },
    "get_quality_records": {
        "method": "GET",
        "path": "/quality/records",
        "param_map": {
            "line_id": "line",
            "defect_type": "defectType",
            "time_range": "period",
        },
        "response_path": "data",
    },
    "get_traceability": {
        "method": "GET",
        "path": "/quality/traceability/{serial_number}",
        "param_map": {
            "serial_number": "serial_number",
        },
        "response_path": "data",
    },
}


class RestConnector(MESConnector):
    """REST API based MES connector.

    Connects to any MES system that exposes HTTP REST APIs.
    Supports configurable endpoint mapping and field translation.

    Example:
        >>> config = MESConnectionConfig(
        ...     mes_type="rest",
        ...     base_url="https://mes.example.com/api/v1",
        ...     auth_type="bearer",
        ...     auth_token="your-token",
        ... )
        >>> connector = RestConnector(config)
        >>> await connector.connect()
        >>> result = await connector.execute_tool("query_production_data", {
        ...     "line_id": "SMT-03",
        ...     "metric": "oee",
        ...     "time_range": "today",
        ... })
    """

    def __init__(
        self,
        config: MESConnectionConfig,
        endpoint_map: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(config)
        self.endpoint_map = endpoint_map or DEFAULT_ENDPOINT_MAP
        self._client: httpx.AsyncClient | None = None

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"ManuGent/{self.config.mes_type}",
        }

        if self.config.auth_type == "bearer" and self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        elif self.config.auth_type == "api_key" and self.config.auth_token:
            headers["X-API-Key"] = self.config.auth_token
        elif self.config.auth_type == "basic":
            import base64
            cred = base64.b64encode(
                f"{self.config.auth_username}:{self.config.auth_password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {cred}"

        return headers

    async def connect(self) -> None:
        """Initialize HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self._build_headers(),
            timeout=self.config.timeout,
        )
        # Verify connection
        try:
            healthy = await self.health_check()
            if healthy:
                self._connected = True
                logger.info(f"Connected to MES at {self.config.base_url}")
            else:
                raise ConnectionError("MES health check failed")
        except Exception as e:
            logger.error(f"Failed to connect to MES: {e}")
            raise

    async def disconnect(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        logger.info("Disconnected from MES")

    async def health_check(self) -> bool:
        """Ping MES health endpoint."""
        if not self._client:
            return False
        try:
            # Try common health endpoints
            for path in ["/health", "/healthz", "/status", "/ping", "/"]:
                try:
                    resp = await self._client.get(path)
                    if resp.status_code < 500:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    async def execute_tool(self, tool_name: str, params: dict[str, Any]) -> QueryResult:
        """Execute a tool by mapping it to an HTTP request."""
        if not self._client:
            return QueryResult(success=False, error="Not connected to MES")

        mapping = self.endpoint_map.get(tool_name)
        if not mapping:
            return QueryResult(
                success=False,
                error=f"Unknown tool: {tool_name}. Available: {list(self.endpoint_map.keys())}",
            )

        try:
            method = mapping["method"].upper()
            path = mapping["path"]
            param_map = mapping.get("param_map", {})
            response_path = mapping.get("response_path", "")

            # Map parameters
            mapped_params = {}
            path_params = {}

            for tool_param, mes_param in param_map.items():
                if tool_param in params:
                    # Check if this param is used in URL path
                    if f"{{{tool_param}}}" in path:
                        path_params[tool_param] = params[tool_param]
                    elif f"{{{mes_param}}}" in path:
                        path_params[mes_param] = params[tool_param]
                    else:
                        mapped_params[mes_param] = params[tool_param]

            # Substitute path parameters
            for key, value in path_params.items():
                path = path.replace(f"{{{key}}}", str(value))

            # Also pass unmapped params that exist
            for key, value in params.items():
                if key not in param_map and f"{{{key}}}" not in mapping["path"]:
                    mapped_params[key] = value

            logger.debug(f"Executing {method} {path} with params: {mapped_params}")

            # Execute request
            if method == "GET":
                resp = await self._client.get(path, params=mapped_params)
            elif method == "POST":
                resp = await self._client.post(path, json=mapped_params)
            else:
                return QueryResult(success=False, error=f"Unsupported HTTP method: {method}")

            resp.raise_for_status()
            data = resp.json()

            # Extract nested response if path specified
            if response_path:
                for key in response_path.split("."):
                    if isinstance(data, dict):
                        data = data.get(key, data)

            return QueryResult(
                success=True,
                data=data,
                metadata={
                    "tool": tool_name,
                    "status_code": resp.status_code,
                    "path": path,
                },
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error executing {tool_name}: {e}")
            return QueryResult(
                success=False,
                error=f"MES API error: {e.response.status_code} - {e.response.text[:200]}",
            )
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return QueryResult(success=False, error=str(e))

    async def get_schema(self) -> dict[str, Any]:
        """Return MES schema for LLM context."""
        if self._schema:
            return self._schema

        schema = {
            "mes_type": self.config.mes_type,
            "base_url": self.config.base_url,
            "available_tools": list(self.endpoint_map.keys()),
            "tool_descriptions": {},
        }

        # Try to fetch schema from MES if available
        for path in ["/schema", "/api-docs", "/swagger.json"]:
            try:
                if self._client:
                    resp = await self._client.get(path)
                    if resp.status_code == 200:
                        schema["mes_api_schema"] = resp.json()
                        break
            except Exception:
                continue

        self._schema = schema
        return schema
