from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.home, name="home"),

    # ✅ TEST URL (Messages check)
    path("test-msg/", views.test_message, name="test_msg"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("create-savings/", views.create_savings, name="create_savings"),
    path("create-business/", views.create_business, name="create_business"),

    path("savings-dashboard/", views.savings_dashboard, name="savings_dashboard"),
    path("business-dashboard/", views.business_dashboard, name="business_dashboard"),

    path("accounts/", views.accounts_list, name="accounts_list"),
    path("transactions/", views.transactions, name="transactions"),
]
