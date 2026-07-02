from flask import Flask, render_template, request, jsonify
from knowledge.vector_store import VectorStore
from config import FLASK_PORT, FLASK_DEBUG, TEMPLATES_DIR

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
store = VectorStore()


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "")
    industry = request.args.get("industry", "")
    time_filter = request.args.get("time", "")
    rating = request.args.get("rating", "")

    result = store.get_reports(
        page=page,
        industry=industry or None,
        rating=rating or None,
        time_filter=time_filter or None,
        query=query or None,
    )
    stats = store.get_stats()
    industries = store.get_industries()

    total_pages = (result["total"] + result["per_page"] - 1) // result["per_page"]
    pagination = {
        "page": page,
        "per_page": result["per_page"],
        "total": result["total"],
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "pages": total_pages,
    }
    filters = {
        "query": query,
        "industry": industry,
        "time": time_filter,
        "rating": rating,
    }

    return render_template(
        "index.html",
        reports=result["reports"],
        stats=stats,
        industries=industries,
        pagination=pagination,
        filters=filters,
    )


@app.route("/report/<int:report_id>")
def report_detail(report_id):
    report = store.get_report(report_id)
    if not report:
        return "研报未找到", 404
    return render_template("report.html", report=report)


@app.route("/api/reports")
def api_reports():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    industry = request.args.get("industry", "")
    rating = request.args.get("rating", "")
    time_filter = request.args.get("time", "")
    query = request.args.get("q", "")

    result = store.get_reports(
        page=page,
        per_page=per_page,
        industry=industry or None,
        rating=rating or None,
        time_filter=time_filter or None,
        query=query or None,
    )
    return jsonify(result)


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "请提供搜索关键词", "results": []}), 400
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    results = store.search(q, top_k=per_page)
    return jsonify({"query": q, "results": results})


@app.route("/api/stats")
def api_stats():
    stats = store.get_stats()
    return jsonify(stats)


@app.route("/api/industries")
def api_industries():
    industries = store.get_industries()
    return jsonify({"industries": industries})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=FLASK_DEBUG)
