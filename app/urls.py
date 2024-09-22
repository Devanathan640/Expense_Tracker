from django.urls import path
from . import views



urlpatterns=[
    path('',views.HomeView.as_view()),
    path('addtennant',views.AddTennant.as_view()),
    path('tennantedit/<int:id>',views.AddTennant.as_view()),
    path('tennantdelete/<int:id>',views.AddTennant.delete_data),
    path('<int:id>',views.AddTennant.as_view()),
    path('addexpense',views.AddExpense.as_view()),
    path('aeedit/<int:id>',views.AddExpense.as_view()),
    path('aedelete/<int:id>',views.AddExpense.delete_data),
    path('calcexpense',views.CalcExpenseView.as_view()),


]
