from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.get_expenses),
    path('add-expense/', views.add_expense),
    path('expenses/delete/<int:id>/', views.delete_expense),
    path('expenses/update/<int:id>/', views.update_expense),
]