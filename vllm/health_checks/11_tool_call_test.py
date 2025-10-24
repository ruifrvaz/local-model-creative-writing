#!/usr/bin/env -S bash -c 'source ~/.venvs/llm/bin/activate && exec python "$0" "$@"'

# Uses OpenAI SDK against vLLM to force a tool call and a final answer.
from openai import OpenAI
import datetime
import json
import sys

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

# Calculator tool - model has to use the result
tools=[{"type":"function","function":{
    "name":"calculate",
    "description":"Performs mathematical calculations. Returns the numerical result of the expression.",
    "parameters":{
        "type":"object",
        "properties":{
            "expression":{"type":"string","description":"Mathematical expression to evaluate (e.g., '25 * 347')"}
        },
        "required":["expression"]
    }
}}]

msgs=[{"role":"user","content":"What is 25 multiplied by 347? Use the calculator tool to get the exact answer."}]

print("=== Tool Calling Test for vLLM ===")
print(f"Model: meta-llama/Llama-3.1-8B-Instruct")
print(f"Tools defined: {len(tools)}")
print()

print("=== Step 1: Requesting tool call (forced) ===")
try:
    # Force the model to call our tool
    r = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=msgs,
        tools=tools,
        tool_choice={"type":"function","function":{"name":"calculate"}},
        temperature=0.0
    )
except Exception as e:
    print(f"[ERROR] Request failed: {e}")
    sys.exit(1)

print(f"✓ Response received")
print(f"  Finish reason: {r.choices[0].finish_reason}")
print(f"  Tool calls: {r.choices[0].message.tool_calls}")

# Check if the model refused or answered directly
if r.choices[0].message.content and not r.choices[0].message.tool_calls:
    print(f"\n[WARNING] Model did not use tools, answered directly:")
    print(f"  Content: {r.choices[0].message.content}")
    print(f"\n[INFO] This may indicate:")
    print(f"  - Model doesn't support tool calling well")
    print(f"  - Server tool-call-parser needs different configuration")
    print(f"  - Try a model known for better tool calling (e.g., gpt-4o format models)")
    sys.exit(1)

if r.choices[0].message.tool_calls:
    call = r.choices[0].message.tool_calls[0]
    print(f"\n=== Step 2: Tool was called ✓ ===")
    print(f"  Tool name: {call.function.name}")
    print(f"  Tool arguments: {call.function.arguments}")
    print(f"  Tool call ID: {call.id}")
    
    # Parse arguments and execute calculation
    args = json.loads(call.function.arguments)
    expression = args.get("expression", "")
    
    print(f"\n=== Step 3: Executing calculator ===")
    print(f"  Expression: {expression}")
    
    # Safely evaluate the expression
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        result_str = str(result)
        print(f"  Result: {result_str}")
    except Exception as e:
        result_str = f"Error: {e}"
        print(f"  Error: {e}")
    
    # Add tool response to conversation
    msgs.append(r.choices[0].message)
    msgs.append({"role":"tool","tool_call_id":call.id,"content":result_str})
    
    print(f"\n=== Step 4: Getting final response ===")
    try:
        final = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct", 
            messages=msgs,
            temperature=0.1
        )
        print(f"✓ Final answer: {final.choices[0].message.content}")
        print(f"\n[SUCCESS] Tool calling workflow completed successfully!")
    except Exception as e:
        print(f"[ERROR] Final response failed: {e}")
        sys.exit(1)
else:
    print("\n[ERROR] No tool call was made!")
    print(f"Message content: {r.choices[0].message.content}")
    sys.exit(1)