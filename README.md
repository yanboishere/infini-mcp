# Infini Payment MCP Server

A Model Context Protocol (MCP) server built on the [Infini Payment API](https://developer.infini.money/docs/) that provides cryptocurrency payment processing capabilities.

## Features

- ✅ **Complete Order Management**: Create, query, list, and reissue tokens
- ✅ **Fund Withdrawal**: Multi-chain withdrawal support
- ✅ **Currency Support**: Get supported cryptocurrency list
- ✅ **Webhook Verification**: Verify callback notification signatures
- ✅ **HMAC-SHA256 Authentication**: Compliant with Infini official signature specifications
- ✅ **Environment Switching**: Support for sandbox and production environments

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Copy the environment template:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your Infini API credentials:

```bash
INFINI_API_KEY=your_api_key_here
INFINI_SECRET_KEY=your_secret_key_here
INFINI_ENV=sandbox  # or production
```

### 3. Run the Server

```bash
uv run server.py
```

## Connect to Infini's MCP Server

### Cursor

To add Infini MCP to Cursor, add the following to your `~/.cursor/mcp.json` file:

```json
{
  "mcpServers": {
    "infini": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/Users/yanbo/infini-mcp"
    }
  }
}
```

To learn more, see the [Cursor documentation](https://docs.cursor.com/).

### VS Code

To add Infini MCP to VS Code, add the following to your `.vscode/mcp.json` file in your workspace:

```json
{
  "servers": {
    "infini": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/Users/yanbo/infini-mcp"
    }
  }
}
```

To learn more, see the [VS Code documentation](https://code.visualstudio.com/docs/).

### Claude Code

To add Infini MCP to Claude Code, run the following command:

```bash
claude mcp add --transport stdio infini uv run server.py
```

To learn more, see the [Claude Code documentation](https://claude.ai/code).

### ChatGPT

To add Infini MCP to ChatGPT, you need to configure it through the ChatGPT interface:

1. Go to Settings > Beta features > MCP Servers
2. Click "Add MCP Server"
3. Select "Local Server"
4. Enter the command: `uv run server.py`
5. Set the working directory: `/Users/yanbo/infini-mcp`

## Available Tools

### Order Management

#### `create_payment_order`
Create a new payment order

**Parameters:**
- `request_id` (str, required): Unique request ID
- `amount` (str, required): Order amount
- `client_reference` (str, optional): Client reference
- `order_desc` (str, optional): Order description
- `merchant_alias` (str, optional): Custom merchant alias
- `expires_in` (int, optional): Expiration time in seconds, 0 for default
- `success_url` (str, optional): Success callback URL
- `failure_url` (str, optional): Failure callback URL

**Returns:** Order details including `order_id` and `checkout_url`

#### `get_payment_order`
Query order details

**Parameters:**
- `order_id` (str, required): Order ID

#### `list_payment_orders`
Get order list

**Parameters:**
- `currency` (str, optional): Currency filter (USDC/USDT)
- `status` (str, optional): Status filter
- `page` (int, optional): Page number, default 1
- `page_size` (int, optional): Page size, default 10

#### `reissue_order_token`
Reissue checkout URL token

**Parameters:**
- `order_id` (str, required): Order ID

### Currency and Funds

#### `get_supported_currencies`
Get supported cryptocurrency list

#### `withdraw_funds`
Withdraw funds to external wallet

**Parameters:**
- `chain` (str, required): Blockchain network
- `token_type` (str, required): Token type
- `amount` (str, required): Withdrawal amount
- `wallet_address` (str, required): Destination wallet address
- `note` (str, optional): Note

### Webhook Verification

#### `verify_webhook_signature`
Verify webhook notification signature

**Parameters:**
- `body` (str, required): Webhook request body
- `signature` (str, required): Signature
- `timestamp` (str, required): Timestamp
- `webhook_secret` (str, optional): Webhook secret

## Error Handling

The server automatically handles common HTTP errors including:

- **400**: Request parameter errors
- **401**: Authentication failure
- **403**: Insufficient permissions
- **404**: Resource not found
- **409**: Business conflicts
- **500**: Internal server errors

## Test Environment

### Test Network

Currently supports **Tron Testnet (Nile)** for testing:

- **Chain**: Tron Testnet
- **Token**: USDT (test coins)
- **Wallet**: TronLink
- **Faucet**: https://nileex.io/join/getJoinPage

### Test Bank Card

Test card number: **4000000000000085** (test environment only)

## Security Tips

1. **Key Security**: API keys and secrets must be securely stored, never expose to frontend
2. **Request Idempotency**: Use globally unique `request_id` to ensure idempotency
3. **Rate Limiting**: Default 600 requests per minute per API Key
4. **Time Synchronization**: Ensure server time accuracy (±300 seconds)

## Development Notes

### Signature Algorithm

This implementation strictly follows Infini official signature specifications:

**Request without Body (GET):**
```
{keyId}
{METHOD} {path}
date: {GMT_time}
```

**Request with Body (POST):**
```
{keyId}
{METHOD} {path}
date: {GMT_time}
digest: SHA-256={body_digest_base64}
```

### Webhook Signature

Webhook uses `timestamp + body` for signature verification.

## Support and Contact

For issues, please refer to [Infini Official Documentation](https://developer.infini.money/docs/) or contact technical support.
