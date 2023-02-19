from flask import Flask, request
import sys
from master_function import generateLearningMaterials
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST", "GET"])
def result():
    print(request.files['filedata'], file=sys.stderr)
    request.files['filedata'].save(request.form["filename"])
    materials = generateLearningMaterials(
            request.form["filename"],
            request.form["output_type"],
            request.form["num_outputs"],
            request.form["grade_level"]
        )
    
    res = {}
    res["Data"] = materials
    print(type(res))

    return res

if __name__ == "__main__":
    app.run(debug=True, port=8000)