import json
import random
from datetime import datetime

class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    def __init__(self):
        # Session Table
        self.sessions = {}  # {session_id: {user_agent, user_ip, country, city, start_time, end_time, mission_id, research_mission_id}}
        
        # Request Table
        self.requests = {}  # {request_id: {session_id, query_string, num_terms, endpoint, timestamp}}
        
        # Click Table
        self.clicks = {}  # {click_id: {session_id, request_id, doc_id, ranking, dwell_time, timestamp}}

        # Fact Clicks (temporary for counting clicks)
        self.fact_clicks = {}  # {doc_id: click_count}

    # SESSION METHODS
    def start_session(self, user_agent: str, user_ip: str, country=None, city=None, mission_id=None, research_mission_id=None) -> int:
        """Start a new session."""
        session_id = random.randint(100000, 999999)
        start_time = datetime.now()
        self.sessions[session_id] = {
            "user_agent": user_agent,
            "user_ip": user_ip,
            "country": country,
            "city": city,
            "start_time": start_time,
            "end_time": None,  # to be updated when session ends
            "mission_id": mission_id,
            "research_mission_id": research_mission_id,
        }
        print(f"Session started: {self.sessions[session_id]}")
        return session_id

    def end_session(self, session_id: int):
        """End an existing session."""
        if session_id in self.sessions:
            self.sessions[session_id]["end_time"] = datetime.now()

    # REQUEST METHODS
    def save_request(self, session_id: int, query_string: str, endpoint: str) -> int:
        """Save a search or request."""
        request_id = random.randint(100000, 999999)
        timestamp = datetime.now()
        num_terms = len(query_string.split())
        self.requests[request_id] = {
            "session_id": session_id,
            "query_string": query_string,
            "num_terms": num_terms,
            "endpoint": endpoint,
            "timestamp": timestamp,
        }
        print(f"Request saved: {self.requests[request_id]}")
        return request_id

    # CLICK METHODS
    def save_click(self, session_id: int, request_id: int, doc_id: int, ranking: int) -> int:
        """Record a document click."""
        click_id = random.randint(100000, 999999)
        timestamp = datetime.now()
        self.clicks[click_id] = {
            "session_id": session_id,
            "request_id": request_id,
            "doc_id": doc_id,
            "ranking": ranking,
            "dwell_time": None,  # to be updated later
            "timestamp": timestamp,
        }

        # Update fact clicks
        if doc_id in self.fact_clicks:
            self.fact_clicks[doc_id] += 1
        else:
            self.fact_clicks[doc_id] = 1

        print(f"Click saved: {self.clicks[click_id]}")
        return click_id

    def update_dwell_time(self, click_id: int, dwell_time: float):
        """Update dwell time for a specific click."""
        if click_id in self.clicks:
            self.clicks[click_id]["dwell_time"] = dwell_time

    # UTILITY METHODS
    def get_session(self, session_id: int):
        """Retrieve session details."""
        return self.sessions.get(session_id)

    def get_request(self, request_id: int):
        """Retrieve request details."""
        return self.requests.get(request_id)

    def get_click(self, click_id: int):
        """Retrieve click details."""
        return self.clicks.get(click_id)

    def get_fact_clicks(self):
        """Get all document click counts."""
        return self.fact_clicks

    # OPTIONAL: Serialize for Debugging
    def to_json(self):
        """Return a JSON representation of the analytics data."""
        return json.dumps({
            "sessions": self.sessions,
            "requests": self.requests,
            "clicks": self.clicks,
            "fact_clicks": self.fact_clicks,
        }, default=str, indent=4)



class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
