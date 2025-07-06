from django.shortcuts import render, redirect
from .models import Transaction, Category
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.utils.safestring import mark_safe


@login_required
def dashboard(request):
    # Base queryset
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.all()

    # Apply filters
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if category_id and category_id != "all":
        transactions = transactions.filter(category_id=category_id)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Calculate totals
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    # Prepare chart data
    category_totals = (
    transactions
    .filter(type='expense')
    .values('category__name')  # Removed 'category__color'
    .annotate(total=Sum('amount'))
    .order_by('-total')
    )

    # Convert to lists for Chart.js
    labels = [item['category__name'] for item in category_totals]
    data = [float(item['total']) for item in category_totals]  # Convert Decimal to float
    colors = [item['category__color'] for item in category_totals] if category_totals[0].get('category__color') else None

    # Prepare context
    context = {
        'transactions': transactions[:10],  # Limit to recent 10 transactions
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
        'chart_labels': mark_safe(json.dumps(labels)),  # Safe JSON
        'chart_data': mark_safe(json.dumps(data)),      # Safe JSON
        'chart_colors': mark_safe(json.dumps(colors)) if colors else None,
    }

    return render(request, 'finance/dashboard.html', context)
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'finance/add_transaction.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after register
            messages.success(request, 'Registration successful! Welcome.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated.")
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'finance/edit_transaction.html', {'form': form})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted.")
        return redirect('dashboard')

    return render(request, 'finance/delete_transaction.html', {'transaction': transaction})