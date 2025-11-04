from flask import Flask, render_template, request, jsonify
from app.Back.controller import process_input

app = Flask(
    __name__,
    template_folder="app/Front/templates",
    static_folder="app/Front/static"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate_route():
    data = request.get_json(force=True)
    input_str = data.get("input", "")
    regex = data.get("regex", "")
    if not regex:
        return jsonify({"error": "No se envió una expresión regular"}), 400
    return jsonify(process_input(input_str, regex))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
