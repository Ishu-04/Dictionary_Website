from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_note/<int:word_id>/', views.add_note, name='add_note'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
