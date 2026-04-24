from django.urls import path
from . import views

urlpatterns = [
    path('', views.trade_list, name='trade_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.trade_create, name='trade_create'),
    path('public/', views.public_trades, name='public_trades'),
    path('<int:trade_id>/', views.trade_detail, name='trade_detail'), #Redirect trade PK
    path('<int:trade_id>/edit/', views.trade_edit, name='trade_edit'), # Edit
    path('<int:trade_id>/delete/', views.trade_delete, name='trade_delete'), #delete

]