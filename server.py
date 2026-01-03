from mcp.server.fastmcp import FastMCP
import httpx
import os
import hmac
import hashlib
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode

# Initialize FastMCP server
mcp = FastMCP("Infini Payment MCP")

# Configuration
INFINI_API_KEY = os.getenv("INFINI_API_KEY")
INFINI_SECRET_KEY = os.getenv("INFINI_SECRET_KEY")
INFINI_ENV = os.getenv("INFINI_ENV", "sandbox")  # sandbox or production

# Base URLs
BASE_URLS = {
    "production": "https://openapi.infini.money",
    "sandbox": "https://openapi-sandbox.infini.money"
}

class InfiniClient:
    def __init__(self):
        self.key_id = INFINI_API_KEY
        self.secret_key = INFINI_SECRET_KEY.encode() if INFINI_SECRET_KEY else None
        self.base_url = BASE_URLS.get(INFINI_ENV, BASE_URLS["sandbox"])
        
        if not self.key_id or not self.secret_key:
            print("Warning: INFINI_API_KEY or INFINI_SECRET_KEY not set.")

    def _sign_request(self, method: str, path: str, body: str = None) -> Dict[str, str]:
        """
        Generate HMAC-SHA256 signature based on Infini documentation.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /order)
            body: JSON body string for POST requests
        
        Returns:
            Dict of headers including Authorization
        """
        gmt_time = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Build signing string
        signing_string = f"{self.key_id}\n{method.upper()} {path}\ndate: {gmt_time}\n"
        
        body_digest_base64 = None
        if body is not None:
            # Calculate body digest
            body_digest = hashlib.sha256(body.encode('utf-8')).digest()
            body_digest_base64 = base64.b64encode(body_digest).decode('utf-8')
            signing_string += f"digest: SHA-256={body_digest_base64}\n"
        
        # Calculate signature
        signature = base64.b64encode(
            hmac.new(self.secret_key, signing_string.encode(), hashlib.sha256).digest()
        ).decode()
        
        # Build headers
        headers = {
            "Date": gmt_time,
            "Authorization": f'Signature keyId="{self.key_id}",algorithm="hmac-sha256",'
                               f'headers="@request-target date",signature="{signature}"'
        }
        
        if body_digest_base64 is not None:
            headers["Digest"] = f"SHA-256={body_digest_base64}"
        
        return headers

    def request(self, method: str, path: str, json_data: Dict = None, params: Dict = None) -> Dict:
        """
        Make HTTP request to Infini API with proper authentication.
        
        Args:
            method: HTTP method
            path: API path
            json_data: Request body for POST requests
            params: Query parameters for GET requests
        
        Returns:
            Response data or error dict
        """
        if not self.key_id or not self.secret_key:
            return {"error": "API credentials not configured"}

        url = f"{self.base_url}{path}"
        
        # Prepare body and headers
        body = None
        if json_data is not None:
            body = json.dumps(json_data, separators=(',', ':'))
        
        headers = self._sign_request(method, path, body)
        
        if json_data is not None:
            headers["Content-Type"] = "application/json"
        
        try:
            with httpx.Client() as client:
                if method.upper() == "GET" and params:
                    url += f"?{urlencode(params)}"
                
                response = client.request(
                    method, 
                    url, 
                    data=body, 
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP Error: {e.response.status_code}",
                "detail": e.response.text
            }
        except Exception as e:
            return {"error": str(e)}

client = InfiniClient()

@mcp.tool()
def create_payment_order(
    request_id: str,
    amount: str,
    client_reference: Optional[str] = None,
    order_desc: Optional[str] = None,
    merchant_alias: Optional[str] = None,
    expires_in: Optional[int] = 0,
    success_url: Optional[str] = None,
    failure_url: Optional[str] = None
) -> str:
    """
    Create a new payment order in Infini.
    
    Args:
        request_id: Unique request ID (UUID recommended)
        amount: Order amount (e.g., "100.00")
        client_reference: Client reference string
        order_desc: Order description
        merchant_alias: Custom merchant alias
        expires_in: Time to live in seconds (0 for default)
        success_url: Success redirect URL
        failure_url: Failure redirect URL
    """
    data = {
        "request_id": request_id,
        "amount": amount
    }
    
    # Add optional fields
    if client_reference:
        data["client_reference"] = client_reference
    if order_desc:
        data["order_desc"] = order_desc
    if merchant_alias:
        data["merchant_alias"] = merchant_alias
    if expires_in is not None:
        data["expires_in"] = expires_in
    if success_url:
        data["success_url"] = success_url
    if failure_url:
        data["failure_url"] = failure_url
        
    result = client.request("POST", "/order", json_data=data)
    return str(result)

@mcp.tool()
def get_payment_order(order_id: str) -> str:
    """
    Get payment order details by order ID.
    
    Args:
        order_id: The order ID to query
    """
    params = {"order_id": order_id}
    result = client.request("GET", "/order", params=params)
    return str(result)

@mcp.tool()
def list_payment_orders(
    currency: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> str:
    """
    List payment orders with optional filters.
    
    Args:
        currency: Filter by currency (USDC/USDT)
        status: Filter by order status
        page: Page number (1 to n)
        page_size: Page size (default 10)
    """
    params = {
        "page": page,
        "page_size": page_size
    }
    
    if currency:
        params["currency"] = currency
    if status:
        params["status"] = status
        
    result = client.request("GET", "/order/list", params=params)
    return str(result)

@mcp.tool()
def reissue_order_token(order_id: str) -> str:
    """
    Reissue checkout URL token for an existing order.
    
    Args:
        order_id: The order ID to reissue token for
    """
    data = {"order_id": order_id}
    result = client.request("POST", "/order/token/reissue", json_data=data)
    return str(result)

@mcp.tool()
def get_supported_currencies() -> str:
    """
    Get list of all supported cryptocurrencies for creating orders.
    """
    result = client.request("GET", "/currency")
    return str(result)

@mcp.tool()
def withdraw_funds(
    chain: str,
    token_type: str,
    amount: str,
    wallet_address: str,
    note: Optional[str] = None
) -> str:
    """
    Withdraw funds to external wallet.
    
    Args:
        chain: Blockchain network name
        token_type: Token identifier
        amount: Amount to withdraw
        wallet_address: Destination wallet address
        note: Optional note
    """
    data = {
        "chain": chain,
        "token_type": token_type,
        "amount": amount,
        "wallet_address": wallet_address
    }
    
    if note:
        data["note"] = note
        
    result = client.request("POST", "/fund/withdraw", json_data=data)
    return str(result)

@mcp.tool()
def verify_webhook_signature(
    body: str,
    signature: str,
    timestamp: str,
    webhook_secret: Optional[str] = None
) -> str:
    """
    Verify webhook signature from Infini.
    
    Args:
        body: Raw webhook body string
        signature: Signature from webhook header
        timestamp: Timestamp from webhook header
        webhook_secret: Webhook secret (uses INFINI_SECRET_KEY if not provided)
    """
    if not webhook_secret:
        webhook_secret = INFINI_SECRET_KEY
    
    if not webhook_secret:
        return "Error: No webhook secret available"
    
    try:
        # Create signing string: timestamp + body
        signing_string = f"{timestamp}{body}"
        
        # Calculate expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                webhook_secret.encode(),
                signing_string.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        # Compare signatures
        if hmac.compare_digest(signature, expected_signature):
            return "Webhook signature verified successfully"
        else:
            return "Webhook signature verification failed"
            
    except Exception as e:
        return f"Error verifying webhook: {str(e)}"

if __name__ == "__main__":
    mcp.run()
