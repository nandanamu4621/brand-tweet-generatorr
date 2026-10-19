
import os
import json
import re
from flask import Flask, render_template, request
from ollama import Client

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "change-this-before-deployment"
)



def build_prompt(data):
    return """
You are a brand social-media strategist.

Brand: {brand}
Industry: {industry}
Campaign objective: {objective}
Products/services: {products}
Preferred tone: {tone}
Example posts: {examples}

Infer a plausible brand voice from the supplied information.
If no example posts are provided, treat the voice as an informed
inference, not verified analysis of the brand's actual accounts.

Generate exactly 10 distinct tweets, ideally under 280 characters.
TONE REQUIREMENTS:
The user's selected tone is: {tone}

All 10 tweets MUST follow the selected tone.
Do NOT include other tones unless the selected tone explicitly asks for a mix.
The "type" field of every tweet must be "{tone}".
Make every tweet consistent with this tone while varying the wording,
hooks, and message.
Do not invent prices, discounts, statistics, product claims, or guarantees.

Return valid JSON only, without Markdown code fences, in this format:
{{
  "voice_summary": [
    "Tone description",
    "Audience description",
    "Themes",
    "Writing style"
  ],
  "tweets": [
        {{"type": "{tone}", "text": "Tweet text"}}
  ]
}}

The tweets array must contain exactly 10 objects.
Each object must have a type and text field.
""".format(
        brand=data.get("brand") or "Not provided",
        industry=data.get("industry") or "Infer from details",
        objective=data.get("objective") or "Engagement and awareness",
        products=data.get("products") or "Not provided",
        tone=data.get("tone") or "Infer a suitable tone",
        examples=data.get("examples") or "None"
    )



@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        data = {
            key: request.form.get(key, "").strip()
            for key in [
                "brand", "industry", "objective",
                "products", "tone", "examples"
            ]
        }

        if not data["brand"] and not data["industry"] and not data["products"]:
            error = "Please enter a brand name, industry, or product details."

        elif not os.getenv("OLLAMA_API_KEY"):
            error = "Ollama API key is missing. Set OLLAMA_API_KEY in your terminal."

        else:
            try:
                print("Connecting to Ollama Cloud...")

                client = Client(
                    host="https://ollama.com",
                    headers={
                        "Authorization": (
                            f"Bearer {os.getenv('OLLAMA_API_KEY')}"
                        )
                    }
                )

                print("Generating 10 tweets...")

                response = client.chat(
                    model="gemma4:31b",
                    messages=[
                        {
                            "role": "user",
                            "content": build_prompt(data)
                        }
                    ],
                    format="json",
                    options={"temperature": 0.7}
                )

                response_text = (response.message.content or "").strip()

                if not response_text:
                    raise ValueError("Ollama returned an empty response.")

                # Remove Markdown fences if the model adds them.
                response_text = re.sub(
                    r"^```(?:json)?\s*",
                    "",
                    response_text,
                    flags=re.IGNORECASE
                )
                response_text = re.sub(
                    r"\s*```$",
                    "",
                    response_text
                ).strip()

                result = json.loads(response_text)

                if not isinstance(result, dict):
                    raise ValueError("The response must be a JSON object.")

                if (
                    not isinstance(result.get("tweets"), list)
                    or len(result["tweets"]) != 10
                ):
                    raise ValueError("The model did not return exactly 10 tweets.")

                if not all(
                    isinstance(tweet, dict)
                    and isinstance(tweet.get("type"), str)
                    and isinstance(tweet.get("text"), str)
                    for tweet in result["tweets"]
                ):
                    raise ValueError("One or more tweets have an invalid format.")

                if not isinstance(result.get("voice_summary"), list):
                    raise ValueError("The voice summary is invalid.")

                print("Successfully generated 10 tweets!")

            except Exception as exc:
                print("Generation failed:", repr(exc))
                result = None
                error = f"Generation failed: {exc}"

    return render_template(
        "index.html",
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )
