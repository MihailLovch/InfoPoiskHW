from flask import Flask, render_template, request
from search import load_index, search, URL_FOR_PARSE

app = Flask(__name__)
index = load_index()


@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "")
        all_results = search(query, index)
        results = all_results[:10]  # ТОП-10

    return render_template("index.html", results=results, query=query, url_base=URL_FOR_PARSE)


if __name__ == "__main__":
    app.run(debug=True)
