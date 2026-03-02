from django.contrib import admin
from .models import SavingsAccount, BusinessAccount, Transaction


@admin.register(SavingsAccount)
class SavingsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "holder_name", "balance", "is_active")
    search_fields = ("holder_name", "user__username")
    list_filter = ("is_active",)


@admin.register(BusinessAccount)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "business_name", "holder_name", "balance", "is_active")
    search_fields = ("business_name", "user__username")
    list_filter = ("is_active",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "account_type", "account_id", "action", "amount", "balance_after", "created_at")
    list_filter = ("account_type", "action")
    search_fields = ("user__username", "account_type", "action")
