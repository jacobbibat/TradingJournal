from django.shortcuts import render, get_object_or_404, redirect
from .models import Trade, BalanceHistory
from .forms import TradeForm, CommentForm, TradeReviewForm, BalanceUpdateForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .decorators import trader_required, analyst_required, admin_required
from django.contrib.auth import login
from .forms import RegisterForm
from .models import Trade

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid(): 
            user = form.save(commit=False) #Create user object but don't save
            user.set_password(form.cleaned_data['password'])
            user.role = 'TRADER'
            user.save()

            login(request, user)
            return redirect('trade_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form
    })

@login_required
def trade_list(request):
    trades = Trade.objects.all().order_by('-trade_date')

    asset = request.GET.get('asset')
    trade_type = request.GET.get('trade_type')
    status = request.GET.get('status')
    visibility = request.GET.get('visibility')

    if asset:
        trades = trades.filter(asset__symbol__icontains=asset)

    if trade_type:
        trades = trades.filter(trade_type=trade_type)

    if status:
        trades = trades.filter(status=status)

    if visibility:
        trades = trades.filter(visibility=visibility)

    return render(request, 'tracker/trade_list.html', {
        'trades': trades,
        'selected_asset': asset,
        'selected_trade_type': trade_type,
        'selected_status': status,
        'selected_visibility': visibility,
    })
@login_required
def trade_detail(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)
    comments = trade.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.trade = trade
            comment.user = request.user
            comment.save()
            return redirect('trade_detail', trade_id=trade.id)
    else:
        form = CommentForm()

    return render(request, 'tracker/trade_detail.html', {
        'trade': trade,
        'comments': comments,
        'form': form,
    })
# Method to create a trade , after save, redirects trade_detail
@login_required
@trader_required
def trade_create(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)

        if form.is_valid():
            trade = form.save(commit=False)
            trade.trader = request.user
            trade.save()
            form.save_m2m()
            return redirect('trade_detail', trade_id=trade.id)
    else:
        form = TradeForm()

    return render(request, 'tracker/trade_form.html', {
        'form': form
    })

@login_required
@trader_required
def trade_edit(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == 'POST':
        form = TradeForm(request.POST, instance=trade)

        if form.is_valid():
            form.save()
            return redirect('trade_detail', trade_id=trade.id)
    else:
        form = TradeForm(instance=trade)

    return render(request, 'tracker/trade_form.html', {
        'form': form
    })

@login_required
@trader_required
def trade_delete(request, trade_id): 
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == 'POST': #Only delete if user confirms
        trade.delete() # Delete from db
        return redirect('trade_list')
    
    return render(request, 'tracker/trade_confirm_delete.html', { # If get req, show this page 
        'trade': trade
    })

@login_required
def dashboard(request):
    trades = Trade.objects.all()

    total_trades = trades.count()
    closed_trades = trades.filter(status='CLOSED')
    winning_trades = closed_trades.filter(profit_loss__gt=0).count()
    losing_trades = closed_trades.filter(profit_loss__lt=0).count()

    total_profit_loss = closed_trades.aggregate(
        total=Sum('profit_loss')
    )['total'] or 0

    win_rate = 0
    if closed_trades.count() > 0:
        win_rate = (winning_trades / closed_trades.count()) * 100

    return render(request, 'tracker/dashboard.html', {
        'total_trades': total_trades,
        'closed_trades': closed_trades.count(),
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': round(win_rate, 2),
    })
@login_required
def public_trades(request):
    trades = Trade.objects.filter(visibility='PUBLIC').order_by('-trade_date')

    return render(request, 'tracker/public_trades.html', {
        'trades' : trades
    })

# Analyst functionality
@login_required
@analyst_required
def review_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == 'POST':
        form = TradeReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.trade = trade
            review.analyst = request.user
            review.save()
            return redirect('trade_detail', trade_id=trade.id)
        else:
            form = TradeReviewForm()

        return render(request, 'tracker/review_trade.html', {
            'trade' : trade,
            'form' : form,
        })

@login_required
@trader_required
def update_balance(request):
    user = request.user # Get current user

    if request.method == "POST":
        form = BalanceUpdateForm(request.POST) # Check if user POST

        if form.is_valid(): #If form is valid, calculate
            old_balance = user.current_balance
            new_balance = form.cleaned_data['new_balance']
            change_amount = new_balance - old_balance

            # Balance history record
            BalanceHistory.objects.create( 
                user=user,
                old_balance=old_balance,
                new_balance=new_balance,
                change_amount=change_amount,
                change_type='ADJUSTMENT',
                reason=form.cleaned_data['reason']
            )

            user.current_balance = new_balance
            user.save()

            return redirect('balance_history')
        
        else:
            #If not, prefill form with current balance
            form = BalanceUpdateForm(initial={
                'new_balance' : user.current_balance
            })

        #render template
        return render(request, 'tracker/update_balance.html', {
            'form' : form
        })
    
@login_required
@trader_required
def balance_history(request):
    history = BalanceHistory.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'tracker/balance_history.html', {
        'history': history
    })

