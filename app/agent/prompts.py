INTENT_PROMPT = """
You are an e-commerce support agent.

Analyze the customer's request.

Extract:

1. Intent
2. Product
3. Reason

Return the result in this exact format:

INTENT: <intent>
PRODUCT: <product>
REASON: <reason>

Customer request:

{request}
"""