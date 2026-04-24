from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.trade_list, name='trade_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.trade_create, name='trade_create'),
    path('public/', views.public_trades, name='public_trades'),
    path('balance/update/', views.update_balance, name='update_balance'),
    path('balance/history/', views.balance_history, name='balance_history'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:asset_id>/edit/', views.asset_edit, name='asset_edit'),
    path('summary/monthly/', views.monthly_summary, name='monthly_summary'),

    path('<int:trade_id>/', views.trade_detail, name='trade_detail'), #Redirect trade PK
    path('<int:trade_id>/edit/', views.trade_edit, name='trade_edit'), # Edit
    path('<int:trade_id>/upload-screenshot/', views.upload_screenshot, name='upload_screenshot'),
    path('screenshots/<int:screenshot_id>/delete/', views.delete_screenshot, name='delete_screenshot'),
    path('<int:trade_id>/delete/', views.trade_delete, name='trade_delete'), #delete
    path('<int:trade_id>/review/', views.review_trade, name='review_trade'),

]