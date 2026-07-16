---
name: bitcoin-ai-tools
description: Access 33+ AI services (image, video, audio, OCR, translation, communication) by paying per request with Bitcoin Lightning — no API keys or signups required.
author: cnghockey
version: "1.0"
tags:
  - ai
  - bitcoin
  - lightning
  - payments
  - image-generation
  - audio
  - video
  - no-signup
---

# Bitcoin AI Tools (Sats4AI)

## Purpose

Use Sats4AI to call specialized AI services — image generation, background removal, TTS, transcription, video, OCR, translation, file conversion, SMS, email, phone calls, and more — paying per request with Bitcoin Lightning micropayments. No API keys, no accounts, no KYC.

## Preconditions

- A Lightning wallet with sats (any wallet: Phoenix, Wallet of Satoshi, Alby, etc.)
- Goose with the Sats4AI MCP server configured, OR direct access to the MCP endpoint

### Add to Goose

The Sats4AI server is a remote streamable-http MCP — no install required:

```
Type: streamable-http
URL: https://sats4ai.com/api/mcp
No environment variables needed
```

Or install via npm:

```bash
npx sats4ai-mcp
```

## Payment Flow

Every tool requires a Lightning micropayment before it runs. The flow is always the same:

1. Call `create_payment` with the tool name and any required parameters → get a Lightning invoice + `paymentId`
2. Pay the invoice with any Lightning wallet (confirms in seconds)
3. Call `check_payment_status({ paymentId })` → wait for `{ paid: true }`
4. Call the tool with `{ paymentId, ...params }` → get the result

Payments are single-use. If the service fails, the payment is marked refundable — call `request_refund({ paymentId })`.

## Available Tools

### Discovery
- `list_models` — browse all tools with pricing (free)
- `get_model_pricing` — check price for a specific tool (free)
- `list_planned_services` — see what's coming next (free)
- `vote_for_service` — vote for a tool to be built (1 sat)

### Image Generation & Editing
- `generate_image` — text-to-image (Grok Imagine, Seedream 4, Nano Banana 2)
- `edit_image` — edit images with natural language instructions

### Image Processing
- `remove_background` — BiRefNet SOTA, handles hair/glass/transparency (5 sats)
- `upscale_image` — 2x/4x Real-ESRGAN super-resolution (5 sats)
- `restore_face` — CodeFormer NeurIPS 2022 face restoration (5 sats)
- `detect_nsfw` — safe/suggestive/explicit classification (2 sats)
- `detect_objects` — bounding boxes + confidence scores via Grounding DINO (5 sats)
- `remove_object` — describe what to remove, no mask needed (15 sats)
- `colorize_image` — black-and-white photo colorization via DDColor (5 sats)
- `deblur_image` — NAFNet ECCV 2022 blur/noise removal (20 sats)

### Video & 3D
- `generate_video` — text-to-video with Kling v3, async (per second)
- `animate_image` — still image to video via Grok Imagine Video, async
- `generate_3d_model` — photo to textured GLB model via Seed3D, async

### Audio
- `text_to_speech` — 467 voices, 45+ languages, emotion control, voice cloning
- `clone_voice` — clone any voice from a single audio sample
- `transcribe_audio` — Mistral Transcription with speaker diarization + timestamps
- `generate_music` — AI vocals and instrumentation via Music-1.5

### Documents & Files
- `extract_document` — PDF/image to Markdown via Mistral OCR
- `extract_receipt` — structured data from receipts and invoices
- `convert_file` — 200+ format conversions
- `merge_pdfs` — merge multiple PDFs preserving bookmarks
- `convert_html_to_pdf` — HTML or Markdown to pixel-perfect PDF
- `epub_to_audiobook` — EPUB/PDF/TXT to M4B audiobook with chapters, async

### Text & Translation
- `generate_text` — frontier LLMs (Kimi K2.5, GPT-OSS-120B, Qwen3-32B)
- `analyze_image` — image understanding via Qwen VL
- `translate_text` — 119 languages via Qwen3-32B

### Communication
- `send_email` — send email to anyone, no SMTP setup
- `send_sms` — send SMS to any phone number, no telecom account
- `place_call` — deliver a spoken message to any phone
- `ai_call` — send an AI voice agent to handle a two-way phone conversation, returns transcript + analysis, async
- `respond_to_ai_call` — answer clarification questions before an AI call proceeds

### Async Job Lifecycle
Some tools (video, 3D, transcription, audiobook, AI calls) are async. They return a `jobId` immediately:
- `check_job_status` — poll until `status: "completed"`
- `get_job_result` — retrieve the final output URL

### Support
- `check_payment_status` — confirm a payment was received
- `request_refund` — request refund for a failed service (free)

## Example Workflow: Remove background from an image

```
1. create_payment({ toolName: "remove_background" })
   → { paymentId: "pay_abc", invoice: "lnbc50n1p...", amountSats: 5 }

2. Pay the Lightning invoice with any wallet

3. check_payment_status({ paymentId: "pay_abc" })
   → { paid: true }

4. remove_background({ paymentId: "pay_abc", imageUrl: "https://example.com/photo.jpg" })
   → { resultUrl: "https://sats4ai.com/results/photo-nobg.png" }
```

## Verification

- [ ] `list_models` returns the tool catalog without payment
- [ ] `create_payment` returns a valid BOLT-11 Lightning invoice
- [ ] After paying, `check_payment_status` returns `{ paid: true }`
- [ ] Tool call with the `paymentId` returns the expected result

## Resources

- Docs: https://sats4ai.com/mcp
- Discovery manifest: https://sats4ai.com/.well-known/mcp
- Tool catalog with pricing: https://sats4ai.com/api/mcp/discovery
- npm: https://www.npmjs.com/package/sats4ai-mcp
