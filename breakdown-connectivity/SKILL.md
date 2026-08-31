---
name: breakdown-connectivity
description: Evidence-first macOS, network, API, and MCP diagnosis with Breakdown.
author: grid-breakdown
version: "1.0"
tags:
  - connectivity
  - network
  - macos
  - api
  - mcp
  - diagnostics
---

# Breakdown Connectivity

Use Breakdown's local MCP server to add current and historical connectivity evidence to an agent's troubleshooting process. Keep the investigation evidence-first: establish the failure and time window, localize the failing segment, then choose the narrowest useful evidence surface.

Breakdown requires macOS 13 or later and the app must be running while its MCP bridge is used.

## When to Use

Use this skill when:

- An agent task is failing or flaky because of Internet, DNS, Wi-Fi, packet loss, latency, routing, endpoint, browser, API, MCP, or cloud-tool connectivity.
- Connectivity should be checked before long or unattended network-dependent work.
- A user-visible outage needs a current or historical connectivity report.
- Breakdown or its local MCP bridge needs to be installed or connected to the client.

Do not use it as a substitute for application-level authentication, authorization, or API debugging when connectivity evidence is healthy and the failure is clearly above the network layer.

## Install the Skill

Install this entry from the Block Agent Skills collection:

```sh
npx skills add https://github.com/block/Agent-Skills --skill breakdown-connectivity
```

The canonical Breakdown package is also available directly for supported Agent Skills clients:

```sh
npx skills add PeaceCraft-LLC/breakdown-agent-connectivity
```

For Claude Code, the canonical upstream package can be installed as a native plugin:

```sh
claude plugin marketplace add PeaceCraft-LLC/breakdown-agent-connectivity
claude plugin install breakdown-connectivity@breakdown
```

## Prerequisites

- macOS 13 or later.
- Breakdown installed from the official download: <https://breakdown.live/download/mac>.
- Breakdown running when the MCP client uses its bridge.
- A connected MCP client, or permission to configure one.

The official agent guide is <https://breakdown.live/for-agents/>. Do not place credentials, bearer tokens, or private configuration in this skill.

## Connect Breakdown

First look for Breakdown MCP tools such as `get_current_network_health` and `list_recent_network_issues`. If they are available, use them directly and skip setup.

If they are unavailable, install Breakdown from the official download page, open the app, and configure the installed bridge. The expected bridge path is:

```text
/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge
```

For Codex:

```sh
codex mcp add breakdown -- "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
```

For Claude Code, use its default scope or choose an explicit scope:

```sh
claude mcp add breakdown -- "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
claude mcp add --scope local breakdown -- "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
claude mcp add --scope project breakdown -- "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
claude mcp add --scope user breakdown -- "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
```

Use only the scope appropriate for the task. For a different stdio MCP client, use an equivalent configuration fragment:

```json
{
  "mcpServers": {
    "breakdown": {
      "command": "/Applications/Breakdown/Breakdown.app/Contents/MacOS/BreakdownMCPBridge"
    }
  }
}
```

Keep Breakdown running, then reload or reconnect the MCP client if required. Setup is complete only when the client's Breakdown tools are discoverable.

## Evidence-First Procedure

1. **Define the failure.** Record the reported symptom, exact timestamp or time window, client/app, endpoint or API operation, and any relevant interface or DNS resolver. Completion criterion: the investigation has a bounded question and time range.
2. **Take a compact snapshot.** Call `get_current_network_health` and, when historical context matters, `list_recent_network_issues`. Completion criterion: current LAN, Internet, app, Internet sub-segment, freshness, and relevant retained issue summaries are recorded.
3. **Localize the failing segment.** Select focused evidence for DNS, Wi-Fi, Ethernet, route, app/service, endpoint, or topology. Prefer bounded windows, result limits, context identifiers, and the smallest useful evidence budget.
   Completion criterion: the evidence distinguishes local access, Internet path, and app/service or endpoint health where possible.
4. **Correlate with the task.** Compare evidence timestamps and identifiers with the reported failure. Treat retained issues as historical until their timestamps overlap the failure; do not assume that a listed issue is current.
   Completion criterion: each conclusion is tied to observed evidence or is explicitly marked uncertain.
5. **Use analysis or a report only when useful.** Use `run_breakdown_analysis` for a synthesized investigation and `export_evidence_report` when a portable artifact is needed.
   Check availability and account limits first; these features may depend on the installed Breakdown version, account level, retained history, and selected context.
   Completion criterion: any analysis is retrieved with `get_breakdown_analysis_result`, and any report is confirmed as available before export.
6. **Report the result.** State the affected layer, evidence window, relevant observations, remaining uncertainty, and the next diagnostic or remediation step. Completion criterion: the user can distinguish network evidence from application or authentication conclusions.

## MCP Tool Selection

Read [references/mcp-tools.md](references/mcp-tools.md) when choosing among Breakdown's evidence and analysis tools. Discover live schemas from the connected server because arguments can evolve.

Compact starting points:

- `get_current_network_health` — current LAN, Internet, App, Internet sub-segment, and freshness status.
- `list_recent_network_issues` — retained issue summaries with severity and context identifiers.
- `get_top_app_health_cards` — compact ranked app and service health.
- `get_endpoint_time_series` — endpoint traffic, loss, round-trip time, and jitter.
- `get_dns_resolver_time_series` — resolver loss, round-trip time, and jitter.
- `get_wifi_interface_time_series` — Wi-Fi signal, link rate, and traffic.
- `get_trace_route_details` — observed path details.
- `get_network_segment_time_series` — LAN, Internet, App, and Internet sub-segment history.

## Pitfalls

- No discoverable Breakdown tools means setup or client connectivity is incomplete; it is not evidence that the network is healthy.
- A current snapshot cannot disprove a past outage. Use a time window and correlate retained issue timestamps.
- A reachable endpoint does not prove API authentication or authorization succeeded. Keep HTTP, application, and credential evidence separate.
- Analysis and Evidence Reports can be unavailable or constrained by Breakdown version, account level, history, or context.
- Do not print or copy authorization headers, tokens, credentials, or unrelated private telemetry into reports or chat.

## Verification

- [ ] Breakdown runs on macOS 13 or later.
- [ ] The MCP client discovers Breakdown tools after setup or reconnect.
- [ ] Current health and recent issues were checked when relevant.
- [ ] Detailed evidence uses a bounded time window and result size.
- [ ] Conclusions are correlated to the failure timestamp and affected app, endpoint, resolver, interface, or route.
- [ ] Network, API, and authentication conclusions are not conflated.
