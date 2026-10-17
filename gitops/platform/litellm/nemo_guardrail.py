"""LiteLLM custom guardrail that calls the NeMo Guardrails check service (D23).

LiteLLM ships no native NeMo hook, so this is the thin adapter. NeMo Guardrails >= 0.23 exposes POST /v1/checks;
0.24 selects the rail set by config_id. Pin the server version: minor releases change this API.
"""
import os

import httpx
from fastapi import HTTPException
from litellm.integrations.custom_guardrail import CustomGuardrail

CHECKS_URL = os.environ.get("NEMO_CHECKS_URL", "http://nemo-guardrails.guardrails.svc.cluster.local:8000/v1/checks")
CONFIG_ID = os.environ.get("NEMO_CONFIG_ID", "agent-platform")


class NemoChecks(CustomGuardrail):
    async def _check(self, role: str, text: str, agent: str | None) -> None:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(CHECKS_URL, json={
                "config_id": CONFIG_ID,
                "messages": [{"role": role, "content": text}],
                "context": {"agent_id": agent},
            })
        resp.raise_for_status()
        result = resp.json()
        # VERIFY against your pinned NeMo version: 0.24 returns a RailOutcome-style status per rail.
        if result.get("status") in ("blocked", "fail"):
            raise HTTPException(status_code=400, detail={"error": "blocked by guardrails", "rails": result.get("rails")})

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        agent = (data.get("metadata") or {}).get("headers", {}).get("x-agent-id")
        for m in data.get("messages", []):
            if isinstance(m.get("content"), str):
                await self._check(m.get("role", "user"), m["content"], agent)
        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        for choice in getattr(response, "choices", []) or []:
            content = getattr(getattr(choice, "message", None), "content", None)
            if content:
                await self._check("assistant", content, None)
        return response
