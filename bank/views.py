from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import SavingsAccount, BusinessAccount, Transaction


# ✅ TEST MESSAGE VIEW (for checking messages working)
def test_message(request):
    messages.success(request, "✅ Messages working boss!")
    return redirect("index")


def index(request):
    return render(request, "bank/index.html")


@login_required
def home(request):
    return render(request, "bank/home.html")


# ✅ REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        p1 = request.POST.get("password1")
        p2 = request.POST.get("password2")

        if p1 != p2:
            messages.error(request, "❌ Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already exists!")
            return redirect("register")

        User.objects.create_user(username=username, password=p1)
        messages.success(request, "✅ Registered successfully! Now login.")
        return redirect("login")

    return render(request, "bank/register.html")


# ✅ LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "❌ Invalid username or password!")
            return redirect("login")

        login(request, user)
        messages.success(request, "✅ Login successful!")
        return redirect("home")

    return render(request, "bank/login.html")


# ✅ LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, "✅ Logged out successfully!")
    return redirect("index")


# ✅ CREATE SAVINGS
@login_required
def create_savings(request):
    if request.method == "POST":
        holder_name = request.POST.get("holder_name")
        balance = request.POST.get("balance")
        pin = request.POST.get("pin")

        if not holder_name or not balance or not pin:
            messages.error(request, "❌ Please fill all fields.")
            return redirect("create_savings")

        SavingsAccount.objects.create(
            user=request.user,
            holder_name=holder_name,
            balance=float(balance),
            pin=int(pin)
        )

        messages.success(request, "✅ Savings account created successfully.")
        return redirect("accounts_list")

    return render(request, "bank/create_savings.html")


# ✅ CREATE BUSINESS
@login_required
def create_business(request):
    if request.method == "POST":
        holder_name = request.POST.get("holder_name")
        business_name = request.POST.get("business_name")
        balance = request.POST.get("balance")

        if not holder_name or not business_name or not balance:
            messages.error(request, "❌ Please fill all fields.")
            return redirect("create_business")

        BusinessAccount.objects.create(
            user=request.user,
            holder_name=holder_name,
            business_name=business_name,
            balance=float(balance)
        )

        messages.success(request, "✅ Business account created successfully.")
        return redirect("accounts_list")

    return render(request, "bank/create_business.html")


# ✅ ACCOUNTS LIST
@login_required
def accounts_list(request):
    savings = SavingsAccount.objects.filter(user=request.user)
    business = BusinessAccount.objects.filter(user=request.user)

    return render(request, "bank/accounts_list.html", {
        "savings": savings,
        "business": business
    })


# ✅ TRANSACTIONS HISTORY
@login_required
def transactions(request):
    tx = Transaction.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "bank/transactions.html", {"tx": tx})


# ✅ SAVINGS DASHBOARD (FULL WORKING)
@login_required
def savings_dashboard(request):
    if request.method == "POST":
        action = request.POST.get("action")
        sid = request.POST.get("sid")
        pin = request.POST.get("pin")
        amount = request.POST.get("amount")

        try:
            savings = SavingsAccount.objects.get(id=sid, user=request.user)
        except SavingsAccount.DoesNotExist:
            messages.error(request, "❌ Savings account not found for your user.")
            return redirect("savings_dashboard")

        pin = int(pin)

        # ✅ CHECK BALANCE
        if action == "check":
            result = savings.check_balance_with_pin(pin)
            if result.startswith("✅"):
                messages.success(request, result)
            else:
                messages.error(request, result)

        # ✅ DEPOSIT
        elif action == "deposit":
            if not amount:
                messages.error(request, "❌ Enter deposit amount.")
            else:
                result = savings.deposit(float(amount))
                if result.startswith("✅"):
                    messages.success(request, result)

                    Transaction.objects.create(
                        user=request.user,
                        account_type="Savings",
                        account_id=savings.id,
                        action="Deposit",
                        amount=float(amount),
                        balance_after=savings.balance
                    )
                else:
                    messages.error(request, result)

        # ✅ WITHDRAW
        elif action == "withdraw":
            if not amount:
                messages.error(request, "❌ Enter withdraw amount.")
            else:
                result = savings.withdraw(float(amount), pin)
                if result.startswith("✅"):
                    messages.success(request, result)

                    Transaction.objects.create(
                        user=request.user,
                        account_type="Savings",
                        account_id=savings.id,
                        action="Withdraw",
                        amount=float(amount),
                        balance_after=savings.balance
                    )
                else:
                    messages.error(request, result)

        # ✅ ATM REQUEST
        elif action == "atm":
            result = savings.request_atm_card()
            if "already" in result.lower():
                messages.warning(request, result)
            else:
                messages.success(request, result)

        # ✅ CHEQUE REQUEST
        elif action == "cheque":
            result = savings.request_cheque()
            if "already" in result.lower():
                messages.warning(request, result)
            else:
                messages.success(request, result)

        # ✅ FREEZE
        elif action == "freeze":
            result = savings.freeze_account()
            if "already" in result.lower():
                messages.warning(request, result)
            else:
                messages.success(request, result)

        # ✅ UNFREEZE
        elif action == "unfreeze":
            result = savings.unfreeze_account()
            if "already" in result.lower():
                messages.warning(request, result)
            else:
                messages.success(request, result)

        else:
            messages.error(request, "❌ Invalid action!")

        return redirect("savings_dashboard")

    return render(request, "bank/savings_dashboard.html")


# ✅ BUSINESS DASHBOARD (FULL WORKING + DEPOSIT ADDED)
@login_required
def business_dashboard(request):
    if request.method == "POST":
        action = request.POST.get("action")
        bid = request.POST.get("bid")
        amount = request.POST.get("amount")

        try:
            business = BusinessAccount.objects.get(id=bid, user=request.user)
        except BusinessAccount.DoesNotExist:
            messages.error(request, "❌ Business account not found for your user.")
            return redirect("business_dashboard")

        # ✅ CHECK BALANCE
        if action == "check":
            result = business.check_balance()
            if result.startswith("✅"):
                messages.success(request, result)
            else:
                messages.error(request, result)

        # ✅ DEPOSIT
        elif action == "deposit":
            if not amount:
                messages.error(request, "❌ Enter deposit amount.")
            else:
                result = business.deposit(float(amount))
                if result.startswith("✅"):
                    messages.success(request, result)

                    Transaction.objects.create(
                        user=request.user,
                        account_type="Business",
                        account_id=business.id,
                        action="Deposit",
                        amount=float(amount),
                        balance_after=business.balance
                    )
                else:
                    messages.error(request, result)

        # ✅ WITHDRAW
        elif action == "withdraw":
            if not amount:
                messages.error(request, "❌ Enter withdraw amount.")
            else:
                result = business.withdraw(float(amount))
                if result.startswith("✅"):
                    messages.success(request, result)

                    Transaction.objects.create(
                        user=request.user,
                        account_type="Business",
                        account_id=business.id,
                        action="Withdraw",
                        amount=float(amount),
                        balance_after=business.balance
                    )
                else:
                    messages.error(request, result)

        # ✅ LOAN
        elif action == "loan":
            if not amount:
                messages.error(request, "❌ Enter loan amount.")
            else:
                result = business.request_loan(float(amount))
                if result.startswith("✅"):
                    messages.success(request, result)

                    Transaction.objects.create(
                        user=request.user,
                        account_type="Business",
                        account_id=business.id,
                        action="Loan Approved",
                        amount=float(amount),
                        balance_after=business.balance
                    )
                else:
                    messages.error(request, result)

        # ✅ CHEQUE
        elif action == "cheque":
            result = business.request_cheque()
            if "already" in result.lower():
                messages.warning(request, result)
            else:
                messages.success(request, result)

        else:
            messages.error(request, "❌ Invalid action!")

        return redirect("business_dashboard")

    return render(request, "bank/business_dashboard.html")
