import requests
import json
import logging
from django.conf import settings
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class GorseClient:
    def __init__(self):
        self.base_url = settings.GORSE_API_URL
        self.api_key = settings.GORSE_API_KEY
        self.headers = {'Content-Type': 'application/json'}
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key

    def _log_response(self, endpoint, response_data, params=None):
        """Helper method to log API responses"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] GORSE API RESPONSE - {endpoint}\n"
        if params:
            log_message += f"Parameters: {json.dumps(params)}\n"
        log_message += f"Response: {json.dumps(response_data, indent=2)}\n"
        log_message += "=" * 50
        logger.info(log_message)
        print(log_message)
        return response_data

    def get_item_details(self, item_id):
        """Fetch detailed item information by ID"""
        endpoint = f"/api/item/{item_id}"
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            self._log_response(endpoint, data)
            # Map fields to a consistent dict
            return {
                'id': data.get('ItemId'),
                'name': data.get('Comment'),
                'categories': data.get('Categories', []),
                'labels': data.get('Labels', []),
                'timestamp': data.get('Timestamp'),
                'is_hidden': data.get('IsHidden'),
            }
        except Exception as e:
            logger.error(f"Error fetching item {item_id}: {e}")
            return None

    def _fetch_and_expand(self, endpoint, params):
        """
        Generic method to fetch a list of item IDs/scores
        and expand each to full item details.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            # print(f"_fetch_and_expand response for endpoint: {endpoint}, params: {params}, response: {response.json()}")
            items = self._log_response(endpoint, response.json(), params)
            # Extract item IDs
            item_ids = []
            for itm in items:
                print(f"itm: {itm}, type: {type(itm)}")
                # Gorse returns dicts with 'Id' or 'ItemId'
                if isinstance(itm, dict):
                    item_ids.append(itm.get('Id') or itm.get('ItemId'))
                elif isinstance(itm, str):
                    item_ids.append(itm)
            # Fetch details for each
            detailed_items = []
            for _id in item_ids:
                details = self.get_item_details(_id)
                if details:
                    detailed_items.append(details)
            # print(f"complete returned detailed_items: {detailed_items}")
            return detailed_items
        except Exception as e:
            logger.error(f"Error fetching from {endpoint}: {e}")
            return []

    def get_recommend_items(self, user_id, category='', n=10, offset=0):
        """Get recommended items for a user"""
        endpoint = f"/api/recommend/{user_id}"
        if category:
            endpoint = f"/api/recommend/{user_id}/{category}"
        params = {'n': n, 'offset': offset}
        return self._fetch_and_expand(endpoint, params)

    def get_latest_items(self, category='', n=10, offset=0):
        """Get latest items (optionally by category) with full details"""
        endpoint = "/api/latest"
        if category:
            endpoint = f"/api/latest/{category}"
        params = {'n': n, 'offset': offset}
        return self._fetch_and_expand(endpoint, params)

    def get_popular_items(self, category='', n=10, offset=0):
        """Get popular items (optionally by category) with full details"""
        endpoint = "/api/popular"
        if category:
            endpoint = f"/api/popular/{category}"
        params = {'n': n, 'offset': offset}
        return self._fetch_and_expand(endpoint, params)

    def get_item_neighbors(self, item_id, category='', n=10, offset=0):
        """Get similar items (optionally by category)"""
        endpoint = f"/api/item/{item_id}/neighbors"
        if category:
            endpoint = f"/api/item/{item_id}/neighbors/{category}"
        params = {'n': n, 'offset': offset}
        return self._fetch_and_expand(endpoint, params)

    def insert_feedback(self, user_id, item_id, feedback_type):
        """Insert user feedback (e.g., purchase, click, like)"""
        endpoint = "/api/feedback"
        url = f"{self.base_url}{endpoint}"
        data = [{
            'UserId': str(user_id),
            'ItemId': item_id,
            'FeedbackType': feedback_type,
            'Timestamp': ''
        }]
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return self._log_response(endpoint, {'status': 'success', 'feedback': data})
        except Exception as e:
            logger.error(f"Error inserting fe'edback: {e}")
            return False

    def insert_item(self, item_data):
        """Insert or update an item in Gorse"""
        endpoint = "/api/item"
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=item_data, headers=self.headers)
            response.raise_for_status()
            return self._log_response(endpoint, {'status': 'success', 'item': item_data})
        except Exception as e:
            logger.error(f"Error inserting item: {e}")
            return False

    def insert_user(self, user_data):
        """Insert or update a user in Gorse"""
        endpoint = "/api/user"
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=user_data, headers=self.headers)
            response.raise_for_status()
            return self._log_response(endpoint, {'status': 'success', 'user': user_data})
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False

    def get_session_recommend(self, user_id, num=10, exclude=None):
        """Get session-based recommendations for a user"""
        endpoint = "/api/session/recommend"
        url = f"{self.base_url}{endpoint}"
        data = {
            'user_id': str(user_id),
            'num': num
        }
        if exclude:
            data['exclude'] = exclude
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return self._log_response(endpoint, response.json())
        except Exception as e:
            logger.error(f"Error getting session recommendations: {e}")
            return []

    def get_session_recommend_by_category(self, category, user_id, num=10, exclude=None):
        """Get session-based recommendations for a user within a specific category"""
        endpoint = f"/api/session/recommend/{category}"
        url = f"{self.base_url}{endpoint}"
        data = {
            'user_id': str(user_id),
            'num': num
        }
        if exclude:
            data['exclude'] = exclude
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return self._log_response(endpoint, response.json())
        except Exception as e:
            logger.error(f"Error getting category session recommendations: {e}")
            return []

    def get_user_neighbors(self, user_id, n=10, offset=0):
        """Get similar users (user neighbors)"""
        endpoint = f"/api/user/{user_id}/neighbors"
        url = f"{self.base_url}{endpoint}"
        params = {'n': n, 'offset': offset}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            print("similar user response:",response)
            response.raise_for_status()
            return self._log_response(endpoint, response.json(), params)
        except Exception as e:
            logger.error(f"Error getting user neighbors: {e}")
            return []
