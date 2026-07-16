---
name: emblemai-crypto-wallet
description: Crypto wallet management across 7 blockchains via EmblemAI. Balance checks, token swaps, portfolio analysis, and transaction execution for Solana, Ethereum, Base, BSC, Polygon, Hedera, and Bitcoin.
author: EmblemCompany
version: "1.0"
tags:
  - crypto
  - wallet
  - blockchain
  - defi
  - trading
  - solana
  - ethereum
---

# EmblemAI Crypto Wallet

Manage crypto wallets through the EmblemAI API across 7 supported blockchains.

## When to Use

- User wants to check crypto wallet balances
- User wants to swap or trade tokens
- User wants portfolio analysis or token research
- User needs cross-chain wallet operations

## Setup

Install the full skill with references and scripts:

```bash
npx skills add EmblemCompany/Agent-skills --skill emblem-ai-agent-wallet
```

Or install the npm package:

```bash
npm install @emblemvault/agentwallet
```

## Supported Chains

| Chain | Operations |
|-------|-----------|
| Solana | Balance, swap, transfer, token lookup |
| Ethereum | Balance, swap, transfer, NFT |
| Base | Balance, swap, transfer |
| BSC | Balance, swap, transfer |
| Polygon | Balance, swap, transfer |
| Hedera | Balance, transfer |
| Bitcoin | Balance, transfer |

## API Integration

Base URL: `https://api.emblemvault.ai`

Authentication requires an API key passed as `x-api-key` header.

### Core Endpoints

- `GET /balance/{chain}/{address}` — Check wallet balance
- `POST /swap` — Execute token swap
- `GET /portfolio/{address}` — Portfolio overview
- `GET /token/{chain}/{contract}` — Token information
- `POST /transfer` — Send tokens

## Key Behaviors

1. **Always confirm** before executing transactions
2. **Check balances first** before attempting swaps or transfers
3. **Verify token contracts** before trading unknown tokens
4. **Report gas estimates** when available
5. **Never expose private keys** — all signing happens server-side

## Links

- [Full skill with references](https://github.com/EmblemCompany/Agent-skills/tree/main/skills/emblem-ai-agent-wallet)
- [npm package](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemAI](https://emblemvault.ai)
