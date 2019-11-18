from django.urls import path
from . import views

urlpatterns = [
    path('get_current_phase/', views.get_current_phase),
    path('add_node/', views.add_node),
    path('get_blockchain/', views.get_blockchain),
    path('get_latest_block/', views.get_latest_block),
    path('merge_transactions/<node>/', views.merge_transactions),
    path('get_transactions/<node>/', views.get_transactions),
    path('add_vote/<node>/', views.add_vote),
]
