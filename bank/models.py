from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50)  # Savings/Business
    account_id = models.IntegerField()
    action = models.CharField(max_length=50)  # Deposit/Withdraw/Loan/etc
    amount = models.FloatField(default=0)
    balance_after = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.amount}"


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    holder_name = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)

    atm_requested = models.BooleanField(default=False)
    cheque_requested = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def check_balance(self):
        if not self.is_active:
            return "❌ Account is inactive / frozen"
        return f"✅ Current Balance: ₹{self.balance}"

    def deposit(self, amount):
        if amount <= 0:
            return "❌ Deposit amount must be greater than 0"
        self.balance += amount
        self.save()
        return f"✅ Deposit Success! New Balance: ₹{self.balance}"

    def request_cheque(self):
        if self.cheque_requested:
            return "⚠️ Cheque Book already requested!"
        self.cheque_requested = True
        self.save()
        return "✅ Cheque Book Request Approved!"

    def freeze_account(self):
        if not self.is_active:
            return "⚠️ Account already frozen!"
        self.is_active = False
        self.save()
        return "✅ Account frozen successfully!"

    def unfreeze_account(self):
        if self.is_active:
            return "⚠️ Account already active!"
        self.is_active = True
        self.save()
        return "✅ Account unfreezed successfully!"


class SavingsAccount(BankAccount):
    pin = models.IntegerField()
    daily_limit = models.FloatField(default=20000)

    def __validate_pin(self, entered_pin):
        return self.pin == entered_pin

    def check_balance_with_pin(self, entered_pin):
        if not self.__validate_pin(entered_pin):
            return "❌ Invalid PIN!"
        return super().check_balance()

    def withdraw(self, amount, entered_pin):
        if not self.__validate_pin(entered_pin):
            return "❌ Invalid PIN!"
        if not self.is_active:
            return "❌ Account is inactive / frozen"
        if amount > self.balance:
            return "❌ Insufficient balance!"
        if amount > self.daily_limit:
            return f"❌ Daily withdrawal limit exceeded! Limit: ₹{self.daily_limit}"

        self.balance -= amount
        self.save()
        return f"✅ Withdraw success! New Balance: ₹{self.balance}"

    def request_atm_card(self):
        if self.atm_requested:
            return "⚠️ ATM Card already requested!"
        self.atm_requested = True
        self.save()
        return "✅ ATM Card request approved!"


class BusinessAccount(BankAccount):
    business_name = models.CharField(max_length=150)
    overdraft_limit = models.FloatField(default=50000)
    loan_limit = models.FloatField(default=200000)

    def withdraw(self, amount):
        if not self.is_active:
            return "❌ Account is inactive / frozen"
        if amount <= 0:
            return "❌ Amount must be greater than 0"
        if amount > (self.balance + self.overdraft_limit):
            return f"❌ Overdraft limit exceeded! Max: ₹{self.balance + self.overdraft_limit}"

        self.balance -= amount
        self.save()
        return f"✅ Withdraw success! New Balance: ₹{self.balance}"

    def request_loan(self, loan_amount):
        if loan_amount <= 0:
            return "❌ Loan amount must be greater than 0"
        if loan_amount > self.loan_limit:
            return f"❌ Loan limit exceeded! Max Loan: ₹{self.loan_limit}"
        return f"✅ Loan Approved! Amount: ₹{loan_amount}"
