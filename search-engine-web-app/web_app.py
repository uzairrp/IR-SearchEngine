import os
from json import JSONEncoder

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine

import matplotlib.pyplot as plt
import io
import base64

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.
file_path = path + "\\farmers-protest-tweets.json"

# file_path = "../../tweets-data-who.json"
corpus = load_corpus(file_path)

# for outputting as dict
print("loaded corpus. first elem:", list(corpus.values())[0])

# for outputting as df
# print("loaded corpus. first elem:", corpus.iloc[0].to_dict())



# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")
    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    # Start session in analytics
    session_id = analytics_data.start_session(
        user_agent=str(agent),
        user_ip=user_ip,
        country=None,  # Optional: Add geolocation if available
        city=None      # Optional: Add geolocation if available
    )
    session['session_id'] = session_id
    print(f"Session started: {analytics_data.get_session(session_id)}")
    print(f"All sessions: {analytics_data.sessions}")
    return render_template('index.html', page_title="Welcome")




@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    session['last_search_query'] = search_query
    print(search_query)
    # Save the search query in analytics
    session_id = session.get('session_id')
    request_id = analytics_data.save_request(
        session_id=session_id,
        query_string=search_query,
        endpoint="/search"
    )
    session['last_request_id'] = request_id
    

    num_docs, results = search_engine.search(search_query, request_id, corpus)

    found_count = num_docs
    session['last_found_count'] = found_count

    print(session)
    print(f"All requests: {analytics_data.requests}")

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    #p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    #Get the doc details
    item = corpus.get(int(clicked_doc_id))
    print(item,"###########")
    # Log the click in analytics
    session_id = session.get("session_id")
    request_id = session.get("last_request_id")
    ranking = int(request.args.get("ranking", 1))  # Optional: Pass ranking of the document
    click_id = analytics_data.save_click(session_id, request_id, int(clicked_doc_id), ranking)
    print(f"Click recorded: {analytics_data.get_click(click_id)}")

    # store data in statistics table 1
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))
    print(f"All clicks: {analytics_data.clicks}")
     # Pass all values to the template
    return render_template('doc_details.html',item = item)

@app.route('/tables', methods=['GET'])
def view_tables():
    # Retrieve the tables data
    sessions = analytics_data.sessions 
    requests = analytics_data.requests  
    clicks = analytics_data.clicks      

    # Pass the data to the tables.html template
    return render_template('tables.html', sessions=sessions, requests=requests, clicks=clicks)

@app.route('/stats', methods=['GET'])
def stats():
    # Retrieve the tables data
    sessions = analytics_data.sessions
    requests = analytics_data.requests
    clicks = analytics_data.clicks

    # Calculate Most Visited Documents
    most_visited_docs = {}
    for click in clicks.values():
        doc_id = click['doc_id']
        most_visited_docs[doc_id] = most_visited_docs.get(doc_id, 0) + 1
    most_visited_docs = sorted(most_visited_docs.items(), key=lambda x: x[1], reverse=True)[:5]

    # Calculate Preferred Browsers
    # 2. Preferred Browsers
    browser_counts = {}
    for session in sessions.values():
        user_agent = session["user_agent"]
        if "Chrome" in user_agent:
            browser = "Chrome"
        elif "Firefox" in user_agent:
            browser = "Firefox"
        elif "Safari" in user_agent:
            browser = "Safari"
        else:
            browser = "Other"
        browser_counts[browser] = browser_counts.get(browser, 0) + 1

    # Calculate Preferred Queries Ranking
    preferred_queries = {}
    for request in requests.values():
        query = request['query_string']
        preferred_queries[query] = preferred_queries.get(query, 0) + 1
    preferred_queries = sorted(preferred_queries.items(), key=lambda x: x[1], reverse=True)[:5]

    # Calculate Average Session Duration
    total_duration = 0
    session_count = 0
    for session in sessions.values():
        start_time = session['start_time']
        end_time = session['end_time']
        if start_time and end_time:
            total_duration += (end_time - start_time).total_seconds()
            session_count += 1
    avg_session_duration = total_duration / session_count if session_count > 0 else 0

    # Calculate Success Rate of Queries
    total_requests = len(requests)
    successful_requests = len(set(click['request_id'] for click in clicks.values()))
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

    return render_template(
        'stats.html',
        most_visited_docs=most_visited_docs,
        preferred_browsers=browser_counts,
        preferred_queries=preferred_queries,
        avg_session_duration=avg_session_duration,
        success_rate=success_rate
    )


@app.route('/dashboard')
def dashboard():
    # Retrieve table data
    sessions = analytics_data.sessions
    requests = analytics_data.requests
    clicks = analytics_data.clicks

    # Graph 1: Most Popular Queries
    query_counts = {}
    for req in requests.values():
        query = req['query_string']
        query_counts[query] = query_counts.get(query, 0) + 1
    sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]  # Top 10
    queries, counts = zip(*sorted_queries) if sorted_queries else ([], [])

    plt.figure(figsize=(10, 5))
    plt.bar(queries, counts)
    plt.xlabel("Query")
    plt.ylabel("Count")
    plt.title("Most Popular Queries")
    plt.xticks(rotation=45, ha='right')

    # Save graph to memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    queries_img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    # Graph 2: Query Success Rate Evolution
    precision_values = []
    relevant_results = 0  # Count of clicks
    total_requests = 0  # Count of requests

    for request_id in sorted(requests):  # Sort requests chronologically
        total_requests += 1
        # Check if this request has clicks
        relevant_results += sum(1 for click in clicks.values() if click['request_id'] == request_id)
        precision = relevant_results / total_requests
        precision_values.append(precision)

    x_axis = list(range(1, total_requests + 1))  # Request numbers as x-axis

    plt.figure(figsize=(10, 5))
    plt.plot(x_axis, precision_values, marker='o')
    plt.xlabel("Number of Requests")
    plt.ylabel("Precision")
    plt.title("Query Success Rate Evolution")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    success_rate_img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return render_template('dashboard.html',
                           queries_url=f"data:image/png;base64,{queries_img}",
                           success_rate_url=f"data:image/png;base64,{success_rate_img}")


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
