from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from main import *

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")


@app.route("/")
def index():
    return render_template("index.html")


@socketio.event
def connect():
    print("client connected.")


@app.route('/query', methods=['POST']) 
# @socketio.on("query")
# def handle_query(form_data):
    # print(form_data)
def handle_query():
    query = request.values["query"]
    qty = request.values["qty"]
    strict = request.values["strict"]
    # query = form_data.get("query")
    # qty = form_data.get("qty")
    # strict = form_data.get("strict")
    if qty == "10":
        qty = None
    html = gsearch(query, results=qty)
    car_urls = get_valid_urls(html)
    keywords = query.split()
    if not strict:
        keywords = []
    urls = []
    for url in car_urls:
        strict_fail = any([kw.lower() not in url for kw in keywords])
        if strict_fail:
            print(f"Skipped {url} [STRICT MODE]")
            continue
        urls.append(url)
    print(urls)
    # emit("urls", urls)
    return jsonify(urls)


# @socketio.on("get_data")
@app.route('/get_data', methods=['POST']) 
# def get_data(url):
def get_data():
    url = request.values["url"]
    print(url)
    html = get_html(url)
    item = get_name_date_price(html)
    if not item:
        print(f"Skipped {url} [INVALID URL]")
        return
    item += tuple([url])
    print(item)
    # emit("item", {"data": item})
    return jsonify(item)


if __name__ == "__main__":
    socketio.run(app,host="0.0.0.0",debug=True)
