"""s3pj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import s3.views as s3_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', s3_view.index, name='index'),
    path('dashboard/', s3_view.DashboardView.as_view()),
    path('code_master/', s3_view.MasterListView.as_view()),
    path('code_master/<int:query_code>/', s3_view.DataListView.as_view()),
    path('stock_list/', s3_view.StockListFullView.as_view()),
    path('sentiment_list/', s3_view.SentimentListView.as_view()),
    path('settings/', s3_view.SettingsView.as_view()),
]
