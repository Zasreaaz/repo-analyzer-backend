import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5"


def run_agent(assignment_text: str, owner: str, repo: str) -> dict:
    from .tools import TOOLS, execute_tool

    system = (
        "You are a teaching assistant that checks whether a GitHub repository "
        "satisfies a school assignment's requirements. You have tools to list and "
        "read files in the repository. Explore only what you need — don't read "
        "every file. When you have enough evidence, stop calling tools and report "
        "your findings."
    )

    messages = [{
        "role": "user",
        "content": (
            f"Assignment requirements:\n{assignment_text}\n\n"
            f"Repository: {owner}/{repo}\n\n"
            "Determine which requirements are implemented, partially implemented, "
            "or missing. Cite the file(s) you checked as evidence for each."
        ),
    }]

    # The loop: keep going until Claude stops asking for tools
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result[:8000],  # cap context growth
                })
        messages.append({"role": "user", "content": tool_results})

    # Second call: force the free-form findings into a structured table
    structured = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=messages + [
            {"role": "user", "content": "Now output your findings as structured data."}
        ],
        output_config={"format": {"type": "json_schema", "schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "requirement": {"type": "string"},
                            "status": {"type": "string", "enum": ["implemented", "partial", "missing"]},
                            "evidence": {"type": "string"},
                        },
                        "required": ["requirement", "status", "evidence"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["requirements"],
            "additionalProperties": False,
        }}},
    )
    text = next(b.text for b in structured.content if b.type == "text")
    return json.loads(text)