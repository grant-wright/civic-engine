from anthropic import AsyncAnthropic
from dataclasses import dataclass


class TokenCost:
    """
    Anthropic API pricing in USD per token.
    Source: https://www.anthropic.com/pricing — update if pricing changes.
    """
    input = 0.000003
    output = 0.000015
    cache_write = 0.00000375
    cache_read = 0.0000003


client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY from env automatically
MODEL = "claude-sonnet-4-6"


@dataclass
class UsageRecord:
    call_type: str  # "map_gen" | "report" | "ai_player" | "faction" | "voice"
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    turn: int
    cycle: int

    @property
    def cost_usd(self) -> float:
        return (
            self.input_tokens         * TokenCost.input
            + self.output_tokens      * TokenCost.output
            + self.cache_write_tokens * TokenCost.cache_write
            + self.cache_read_tokens  * TokenCost.cache_read
        )


usage_log: list[UsageRecord] = []


def record_usage(call_type: str, response, turn: int = 0, cycle: int = 1) -> None:
    u = response.usage
    usage_log.append(
        UsageRecord(
            call_type=call_type,
            input_tokens=u.input_tokens,
            output_tokens=u.output_tokens,
            cache_write_tokens=u.cache_creation_input_tokens or 0,
            cache_read_tokens=u.cache_read_input_tokens or 0,
            turn=turn,
            cycle=cycle,
        )
    )


async def safe_claude_call(kwargs: dict, fallback_tokens: int, call_type: str = "unknown"):
    """Call Claude; if response is truncated, record the attempt and retry with more tokens."""
    response = await client.messages.create(**kwargs)
    if response.stop_reason == "max_tokens":
        record_usage(f"{call_type}_truncated", response)
        kwargs["max_tokens"] = fallback_tokens
        response = await client.messages.create(**kwargs)
    return response
