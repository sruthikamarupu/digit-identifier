import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

client = genai.Client(api_key=API_KEY)

app = Flask(__name__)
CORS(app)  

@app.route("/identify", methods=["POST"])
def identify_number():

    f = request.files["image"]
    try:
        img_bytes = f.read()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=img_bytes,
                    mime_type="image/png",
                ),
                "Identify this number, just give me the number alone, if you cant identify the number, give nan"
            ],
        )

        number_text = None
        try:
            number_text = response.candidates[0].content.parts[0].text
        except Exception:
        
            number_text = str(response)

        number_text = (number_text or "").strip()

        import re
        digits = re.findall(r"\d+", number_text)
        if digits:
            result = digits[0]  
        else:
            if number_text.lower().startswith("nan") or number_text.lower() in ("nan", "n/a", "none"):
                result = "nan"
            else:
                result = "nan"

        return jsonify({"number": result})

    except Exception as e:
        return jsonify({"error": str(e), "number": "nan"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)