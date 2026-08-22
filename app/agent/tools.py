import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from pydantic import create_model

from armoriq_sdk import ArmorIQClient


load_dotenv()


class MCPToolManager:

    def __init__(self, client):

        # Your normal MCP client
        self.client = client

        # ArmorIQ client
        # Reads ARMORIQ_API_KEY from environment / ArmorIQ credentials
        self.armoriq = ArmorIQClient.from_config("armoriq.yaml")

        # IMPORTANT:
        # These names MUST exactly match the MCP names
        # registered in ArmorIQ Inventory.
        self.mcp_mapping = {
            "commerce": "commerce1",
            "fulfillment": "fulfillment",
            "payment": "payment",
        }

        # End-user identity used by ArmorIQ policy enforcement
        #
        # Put an actual email here that matches the
        # "Applies to" setting of your ArmorIQ policies.
        self.user_email = os.getenv(
            "ARMORIQ_USER_EMAIL",
            "customer@example.com",
        )

    # ---------------------------------------------------------
    # Convert MCP JSON schema -> Pydantic model
    # ---------------------------------------------------------

    def build_args_schema(self, tool_name, input_schema):

        properties = input_schema.get(
            "properties",
            {},
        )

        required = input_schema.get(
            "required",
            [],
        )

        fields = {}

        for field_name, field_info in properties.items():

            json_type = field_info.get("type")

            # Basic JSON -> Python type conversion
            if json_type == "string":
                field_type = str

            elif json_type == "integer":
                field_type = int

            elif json_type == "number":
                field_type = float

            elif json_type == "boolean":
                field_type = bool

            elif json_type == "array":
                field_type = list

            elif json_type == "object":
                field_type = dict

            else:
                field_type = Any

            # Required field
            if field_name in required:

                fields[field_name] = (
                    field_type,
                    ...,
                )

            # Optional field
            else:

                default = field_info.get(
                    "default",
                    None,
                )

                fields[field_name] = (
                    field_type | None,
                    default,
                )

        return create_model(
            f"{tool_name}Input",
            **fields,
        )

    # ---------------------------------------------------------
    # Extract ArmorIQ result safely
    # ---------------------------------------------------------

    def extract_result(self, result):

        print()
        print("========== ARMORIQ RAW RESULT ==========")
        print(type(result))
        print(result)

        # ---------------------------------------------
        # Case 1: result has .data
        # ---------------------------------------------

        if hasattr(result, "data"):

            data = result.data

            print()
            print("[ArmorIQ] Result data:")
            print(data)

            return self.convert_to_text(data)

        # ---------------------------------------------
        # Case 2: result has .result
        # ---------------------------------------------

        if hasattr(result, "result"):

            mcp_result = result.result

            print()
            print("[ArmorIQ] Nested result:")
            print(mcp_result)

            if hasattr(
                mcp_result,
                "content",
            ):

                content = mcp_result.content

                if content:

                    return self.convert_to_text(
                        content
                    )

            return str(mcp_result)

        # ---------------------------------------------
        # Case 3: direct MCP result
        # ---------------------------------------------

        if hasattr(result, "content"):

            content = result.content

            if content:

                return self.convert_to_text(
                    content
                )

        # ---------------------------------------------
        # Case 4: Pydantic model
        # ---------------------------------------------

        if hasattr(
            result,
            "model_dump",
        ):

            try:

                dumped = result.model_dump()

                print()
                print("[ArmorIQ] Model dump:")
                print(dumped)

                return str(dumped)

            except Exception:
                pass

        # ---------------------------------------------
        # Fallback
        # ---------------------------------------------

        return str(result)

    # ---------------------------------------------------------
    # Convert MCP content into readable text
    # ---------------------------------------------------------

    def convert_to_text(self, data):

        if isinstance(data, str):
            return data

        if isinstance(data, list):

            output = []

            for item in data:

                if isinstance(item, dict):

                    if "text" in item:
                        output.append(
                            item["text"]
                        )

                    else:
                        output.append(
                            str(item)
                        )

                elif hasattr(item, "text"):

                    output.append(
                        item.text
                    )

                else:

                    output.append(
                        str(item)
                    )

            return "\n".join(output)

        return str(data)

    # ---------------------------------------------------------
    # Get all MCP tools
    # ---------------------------------------------------------

    async def get_tools(self):

        mcp_tools = await self.client.list_tools()

        tools = []

        for server_name, server_tools in mcp_tools.items():

            for mcp_tool in server_tools:

                tool_name = mcp_tool.name

                description = (
                    mcp_tool.description
                    or "MCP tool"
                )

                input_schema = (
                    mcp_tool.input_schema
                    or {}
                )

                # -----------------------------------------
                # Create Pydantic schema
                # -----------------------------------------

                ArgsSchema = self.build_args_schema(
                    tool_name,
                    input_schema,
                )

                # -----------------------------------------
                # Capture values for closure
                # -----------------------------------------

                async def execute(
                    server=server_name,
                    name=tool_name,
                    **kwargs,
                ):

                    # -------------------------------------
                    # ArmorIQ MCP name
                    # -------------------------------------

                    armor_mcp = self.mcp_mapping.get(
                        server
                    )

                    if armor_mcp is None:

                        raise RuntimeError(
                            f"No ArmorIQ MCP mapping found "
                            f"for server '{server}'"
                        )

                    print()
                    print("=" * 60)
                    print(
                        "[ArmorIQ] TOOL REQUEST"
                    )
                    print("=" * 60)

                    print(
                        f"MCP       : {armor_mcp}"
                    )

                    print(
                        f"Action    : {name}"
                    )

                    print(
                        f"Parameters: {kwargs}"
                    )

                    print(
                        f"User      : {self.user_email}"
                    )

                    print("=" * 60)

                    try:

                        # ---------------------------------
                        # 1. Create ArmorIQ plan
                        # ---------------------------------

                        plan_definition = {

                            "goal": (
                                "Resolve the customer's "
                                "e-commerce request"
                            ),

                            "steps": [

                                {
                                    "action": name,
                                    "mcp": armor_mcp,
                                    "params": kwargs,
                                }

                            ],
                        }

                        print(
                            "\n[ArmorIQ] Capturing plan..."
                        )

                        captured_plan = (
                            self.armoriq.capture_plan(
                                llm="gemini-2.5-flash",
                                prompt=(
                                    f"Execute the e-commerce "
                                    f"action '{name}' using "
                                    f"the provided parameters."
                                ),
                                plan=plan_definition,
                            )
                        )

                        print(
                            "[ArmorIQ] ✓ Plan captured"
                        )

                        # ---------------------------------
                        # 2. Generate signed intent token
                        # ---------------------------------

                        print(
                            "[ArmorIQ] Creating intent token..."
                        )

                        token = (
                            self.armoriq.get_intent_token(
                                captured_plan,
                                validity_seconds=300,
                            )
                        )

                        print(
                            "[ArmorIQ] ✓ Intent token created"
                        )

                        # ---------------------------------
                        # 3. Invoke through ArmorIQ
                        # ---------------------------------

                        print()
                        print(
                            "[ArmorIQ] Calling policy engine..."
                        )

                        result = self.armoriq.invoke(

                            mcp=armor_mcp,

                            action=name,

                            intent_token=token,

                            params=kwargs,

                            user_email=self.user_email,
                        )

                        print()
                        print(
                            "[ArmorIQ] ✓ Invocation completed"
                        )

                        # ---------------------------------
                        # 4. Extract result
                        # ---------------------------------

                        return self.extract_result(
                            result
                        )

                    except Exception as e:

                        # ---------------------------------
                        # ArmorIQ blocked / failed
                        # ---------------------------------

                        print()
                        print("=" * 60)
                        print(
                            "[ArmorIQ] ✗ INVOCATION FAILED"
                        )
                        print("=" * 60)

                        print(
                            f"Tool : {armor_mcp}.{name}"
                        )

                        print(
                            f"Error: {type(e).__name__}"
                        )

                        print(
                            f"Details: {str(e)}"
                        )

                        print("=" * 60)

                        # Return error to LangGraph
                        # rather than killing the graph
                        return (
                            f"ArmorIQ blocked or failed "
                            f"the tool call "
                            f"{armor_mcp}.{name}. "
                            f"Reason: {str(e)}"
                        )

                # -----------------------------------------
                # Create LangChain StructuredTool
                # -----------------------------------------

                tool = StructuredTool.from_function(

                    coroutine=execute,

                    name=tool_name,

                    description=description,

                    args_schema=ArgsSchema,
                )

                tools.append(tool)

        return tools