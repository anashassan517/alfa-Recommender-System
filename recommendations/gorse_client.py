# import requests
# from django.conf import settings

# class GorseClient:
#     def __init__(self):
#         self.base_url = settings.GORSE_API_URL
#         self.api_key = settings.GORSE_API_KEY
#         self.headers = {}
#         if self.api_key:
#             self.headers['X-API-Key'] = self.api_key
    
#     def get_recommend_items(self, user_id, category='', n=10):
#         """
#         Get recommended items for a user
#         """
#         url = f"{self.base_url}/api/recommend/{user_id}"
#         params = {'n': n}
#         if category:
#             params['category'] = category
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error getting recommendations: {e}")
#             return []
    
#     def get_popular_items(self, category='', n=10):
#         """
#         Get popular items
#         """
#         url = f"{self.base_url}/api/popular"
#         params = {'n': n}
#         if category:
#             params['category'] = category
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error getting popular items: {e}")
#             return []
    
#     def insert_feedback(self, user_id, item_id, feedback_type):
#         """
#         Insert user feedback (e.g., purchase, click, like)
#         """
#         url = f"{self.base_url}/api/feedback"
#         data = {
#             'user_id': user_id,
#             'item_id': item_id,
#             'feedback_type': feedback_type
#         }
        
#         try:
#             response = requests.post(url, json=data, headers=self.headers)
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"Error inserting feedback: {e}")
#             return False


### works well
# import requests
# from django.conf import settings

# class GorseClient:
#     def __init__(self):
#         self.base_url = settings.GORSE_API_URL
#         self.api_key = settings.GORSE_API_KEY
#         self.headers = {}
#         if self.api_key:
#             self.headers['X-API-Key'] = self.api_key
    
#     def get_recommend_items(self, user_id, category='', n=10):
#         """
#         Get recommended items for a user
#         """
#         url = f"{self.base_url}/api/recommend/{user_id}"
#         params = {'n': n}
#         if category:
#             params['category'] = category
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error getting recommendations: {e}")
#             return []
    
#     def get_popular_items(self, category='', n=10):
#         """
#         Get popular items
#         """
#         url = f"{self.base_url}/api/popular"
#         params = {'n': n}
#         if category:
#             params['category'] = category
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error getting popular items: {e}")
#             return []
    
#     def insert_feedback(self, user_id, item_id, feedback_type):
#         """
#         Insert user feedback (e.g., purchase, click, like)
#         """
#         url = f"{self.base_url}/api/feedback"
#         data = {
#             'user_id': str(user_id),
#             'item_id': item_id,
#             'feedback_type': feedback_type,
#             'timestamp': ''  # Current time will be used by Gorse
#         }
        
#         try:
#             response = requests.post(url, json=data, headers=self.headers)
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"Error inserting feedback: {e}")
#             return False
    
#     def insert_item(self, item_data):
#         """
#         Insert or update an item in Gorse
#         """
#         url = f"{self.base_url}/api/item"
#         try:
#             response = requests.post(url, json=item_data, headers=self.headers)
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"Error inserting item: {e}")
#             return False
            
#     def get_similar_items(self, item_id, n=10):
#         """
#         Get similar items
#         """
#         url = f"{self.base_url}/api/item/{item_id}/neighbors"
#         params = {'n': n}
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"Error getting similar items: {e}")
#             return []

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
            logger.error(f"Error inserting feedback: {e}")
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


# import requests
# import json
# import logging
# from django.conf import settings
# from datetime import datetime

# # Set up logging
# logger = logging.getLogger(__name__)

# class GorseClient:
#     def __init__(self):
#         self.base_url = settings.GORSE_API_URL
#         self.api_key = settings.GORSE_API_KEY
#         self.headers = {'Content-Type': 'application/json'}
#         if self.api_key:
#             self.headers['X-API-Key'] = self.api_key
    
#     def _log_response(self, endpoint, response_data, params=None):
#         """Helper method to log API responses"""
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         log_message = f"[{timestamp}] GORSE API RESPONSE - {endpoint}\n"
#         if params:
#             log_message += f"Parameters: {json.dumps(params)}\n"
#         log_message += f"Response: {json.dumps(response_data, indent=2)}\n"
#         log_message += "=" * 50
        
#         logger.info(log_message)
#         print(log_message)  # Also print to console for immediate visibility
#         return response_data
    
#     # Personalized recommendations
#     def get_recommend_items(self, user_id, category='', n=10, offset=0):
#         """Get recommended items for a user"""
#         endpoint = f"/api/recommend/{user_id}"
#         if category:
#             endpoint = f"/api/recommend/{user_id}/{category}"
        
#         url = f"{self.base_url}{endpoint}"
#         params = {'n': n, 'offset': offset}
        
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             print("get recommendation_items response for user_id: ", user_id, " response: ", response.json())
#             return self._log_response(endpoint, response.json(), params)
#         except Exception as e:
#             logger.error(f"Error getting recommendations: {e}")
#             print(f"Error getting recommendations: {e}")
#             return []
    
#     # Latest items
#     def get_latest_items(self, category='', n=10, offset=0):
#         """Get latest items (optionally by category)"""
#         endpoint = "/api/latest"
#         if category:
#             endpoint = f"/api/latest/{category}"
        
#         url = f"{self.base_url}{endpoint}"
#         params = {'n': n, 'offset': offset}
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return self._log_response(endpoint, response.json(), params)
#         except Exception as e:
#             logger.error(f"Error getting latest items: {e}")
#             print(f"Error getting latest items: {e}")
#             return []
    
#     # Popular items
#     def get_popular_items(self, category='', n=10, offset=0):
#         """Get popular items (optionally by category)"""
#         endpoint = "/api/popular"
#         if category:
#             endpoint = f"/api/popular/{category}"
        
#         url = f"{self.base_url}{endpoint}"
#         params = {'n': n, 'offset': offset}
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return self._log_response(endpoint, response.json(), params)
#         except Exception as e:
#             logger.error(f"Error getting popular items: {e}")
#             print(f"Error getting popular items: {e}")
#             return []
    
#     # Item neighbors (similar items)
#     def get_item_neighbors(self, item_id, category='', n=10, offset=0):
#         """Get similar items (optionally by category)"""
#         endpoint = f"/api/item/{item_id}/neighbors"
#         if category:
#             endpoint = f"/api/item/{item_id}/neighbors/{category}"
        
#         url = f"{self.base_url}{endpoint}"
#         params = {'n': n, 'offset': offset}
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return self._log_response(endpoint, response.json(), params)
#         except Exception as e:
#             logger.error(f"Error getting item neighbors: {e}")
#             print(f"Error getting item neighbors: {e}")
#             return []
    
#     # Dashboard item neighbors
#     def get_dashboard_item_neighbors(self, item_id, n=10, offset=0):
#         """Get dashboard neighbors data for an item"""
#         endpoint = f"/api/item/{item_id}/neighbors"
        
#         url = f"{self.base_url}{endpoint}"
#         params = {'n': n, 'offset': offset}
        
#         try:
#             response = requests.get(url, headers=self.headers, params=params)
#             response.raise_for_status()
#             return self._log_response(endpoint, response.json(), params)
#         except Exception as e:
#             logger.error(f"Error getting dashboard item neighbors: {e}")
#             print(f"Error getting dashboard item neighbors: {e}")
#             return []
    
#     # User feedback
#     def insert_feedback(self, user_id, item_id, feedback_type):
#         """Insert user feedback (e.g., purchase, click, like)"""
#         endpoint = "/api/feedback"
#         url = f"{self.base_url}{endpoint}"
        
#         data = [{
#             'UserId': str(user_id),
#             'ItemId': item_id,
#             'FeedbackType': feedback_type,
#             'Timestamp': ''  # Current time will be used by Gorse
#         }]
        
#         try:
#             response = requests.post(url, json=data, headers=self.headers)
#             response.raise_for_status()
#             return self._log_response(endpoint, {"status": "success", "feedback": data})
#         except Exception as e:
#             logger.error(f"Error inserting feedback: {e}")
#             print(f"Error inserting feedback: {e}")
#             return False
    
#     # Item management
#     def insert_item(self, item_data):
#         """Insert or update an item in Gorse"""
#         endpoint = "/api/item"
#         url = f"{self.base_url}{endpoint}"
        
#         try:
#             response = requests.post(url, json=item_data, headers=self.headers)
#             response.raise_for_status()
#             return self._log_response(endpoint, {"status": "success", "item": item_data})
#         except Exception as e:
#             logger.error(f"Error inserting item: {e}")
#             print(f"Error inserting item: {e}")
#             return False
    
#     # Add this helper method to the GorseClient class
# def _log_and_extract_item_ids(self, endpoint, response_data, params=None):
#     """Helper method to log API responses and extract item IDs from the response"""
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     log_message = f"[{timestamp}] GORSE API RESPONSE - {endpoint}\n"
#     if params:
#         log_message += f"Parameters: {json.dumps(params)}\n"
    
#     # Print the raw response structure to help with debugging
#     log_message += f"Response Type: {type(response_data)} with {len(response_data)} items\n"
#     if response_data and len(response_data) > 0:
#         log_message += f"First item type: {type(response_data[0])}\n"
#         log_message += f"First item: {json.dumps(response_data[0] if isinstance(response_data[0], dict) else response_data[0])}\n"
    
#     log_message += f"Full Response: {json.dumps(response_data, indent=2)}\n"
#     log_message += "=" * 50
    
#     logger.info(log_message)
#     print(log_message)  # Also print to console for immediate visibility
    
#     # Extract and return item IDs
#     item_ids = []
#     for item in response_data:
#         if isinstance(item, dict) and 'ItemId' in item:
#             item_ids.append(item['ItemId'])
#         elif isinstance(item, str):
#             item_ids.append(item)
    
#     return item_ids