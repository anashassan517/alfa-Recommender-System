from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Main recommendation pages
    path('for-you/', views.user_recommendations, name='user_recommendations'),
    path('latest/', views.latest_items, name='latest_items'),
    path('popular/', views.popular_items, name='popular_items'),
    path('similar/<int:product_id>/', views.similar_items, name='similar_items'),
    path('explore/', views.explore_recommendations, name='explore'),
    path('dashboard-neighbors/<int:product_id>/', views.dashboard_item_neighbors, name='dashboard_neighbors'),
    
    # API for AJAX recommendations
    path('api/get-recommendations/', views.get_recommendations_json, name='get_recommendations_json'),
    
    # New URL patterns
    path('similar-users/', views.user_neighbors, name='user_neighbors'),
    path('api/session/recommend/', views.api_session_recommend, name='api_session_recommend'),
    path('api/session/recommend/<str:category>/', views.api_session_recommend_by_category, name='api_session_recommend_by_category'),
    
    # API to get user recommendations with product details
    path('api/user/<str:user_id>/recommendations/', views.api_user_recommendations, name='api_user_recommendations'),
]