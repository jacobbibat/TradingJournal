from django.shortcuts import render, get_object_or_404, redirect
from .models import Trade, BalanceHistory, Asset, TradeScreenshot
from .forms import TradeForm, CommentForm, TradeReviewForm, BalanceUpdateForm, RegisterForm, AssetForm, TradeScreenshotForm
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .decorators import trader_required, analyst_required, admin_required
from django.contrib.auth import login

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

    return render(request, 'tracker/register.html', {
        'form': form
    })

@login_required
def trade_list(request):
    trades = Trade.objects.filter(trader=request.user).order_by('-trade_date') # Now only linked to trader who owns it

    asset = request.GET.get('asset')
    trade_type = request.GET.get('trade_type')
    status = request.GET.get('status')
    visibility = request.GET.get('visibility')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if asset:
        trades = trades.filter(asset__symbol__icontains=asset)

    if trade_type:
        trades = trades.filter(trade_type=trade_type)

    if status:
        trades = trades.filter(status=status)

    if visibility:
        trades = trades.filter(visibility=visibility)
            
    if start_date:
        trades = trades.filter(trade_date__date__gte=start_date)

    if end_date:
        trades = trades.filter(trade_date__date__lte=end_date)

    return render(request, 'tracker/trade_list.html', {
        'trades': trades,
        'selected_asset': asset,
        'selected_trade_type': trade_type,
        'selected_status': status,
        'selected_visibility': visibility,
        'selected_start_date' : start_date,
        'selected_end_date' : end_date,
    })

@login_required
def trade_detail(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)
    comments = trade.comments.all().order_by('-created_at')

    if trade.visibility == 'PRIVATE' and trade.trader != request.user: #Only visible to owner if private
        return redirect('trade_list')

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
    trade = get_object_or_404(Trade, id=trade_id, trader=request.user)

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
    trade = get_object_or_404(Trade, id=trade_id, trader=request.user)

    if request.method == 'POST': #Only delete if user confirms
        trade.delete() # Delete from db
        return redirect('trade_list')
    
    return render(request, 'tracker/trade_confirm_delete.html', { # If get req, show this page 
        'trade': trade
    })

@login_required
def dashboard(request):
    trades = Trade.objects.filter(trader=request.user)

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

        # Chart Data
        'win_loss_labels' : ['Winning Trades', 'Losing Trades'],
        'win_loss_data' : [winning_trades, losing_trades],
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
        'trade': trade,
        'form': form,
    })

@login_required
@trader_required
def update_balance(request):
    user = request.user

    if request.method == "POST":
        form = BalanceUpdateForm(request.POST)

        if form.is_valid():
            old_balance = user.current_balance
            new_balance = form.cleaned_data['new_balance']
            change_amount = new_balance - old_balance

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
        form = BalanceUpdateForm(initial={
            'new_balance': user.current_balance
        })

    return render(request, 'tracker/update_balance.html', {
        'form': form
    })
    
@login_required
@trader_required
def balance_history(request):
    history = BalanceHistory.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'tracker/balance_history.html', {
        'history': history
    })

@login_required
@admin_required
def asset_list(request):
    assets = Asset.objects.all().order_by('symbol')

    return render(request, 'tracker/asset_list.html', {
        'assets': assets
    })

@login_required
@admin_required
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm()

    return render(request, 'tracker/asset_form.html', {
        'form': form
    })

@login_required
@admin_required
def asset_edit(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)

        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)

    return render(request, 'tracker/asset_form.html', {
        'form': form
    })

@login_required
@trader_required
def upload_screenshot(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, trader=request.user)

    if request.method == 'POST':
        form = TradeScreenshotForm(request.POST, request.FILES)

        if form.is_valid():
            screenshot = form.save(commit=False)
            screenshot.trade = trade
            screenshot.save()
            return redirect('trade_detail', trade_id=trade.id)
    else:
        form = TradeScreenshotForm()

    return render(request, 'tracker/upload_screenshot.html', {
        'form': form,
        'trade': trade
    })

@login_required
@trader_required
def delete_screenshot(request, screenshot_id):
    screenshot = get_object_or_404(
        TradeScreenshot,
        id=screenshot_id,
        trade__trader=request.user
    )

    trade_id = screenshot.trade.id

    if request.method == 'POST':
        screenshot.delete()
        return redirect('trade_detail', trade_id=trade_id)

    return render(request, 'tracker/delete_screenshot.html', {
        'screenshot': screenshot
    })

@login_required
def monthly_summary(request):
    today = timezone.now()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    trades = Trade.objects.filter(
        trader=request.user,
        trade_date__year=year,
        trade_date__month=month,
        status='CLOSED'
    )

    total_trades = trades.count()
    winning_trades = trades.filter(profit_loss__gt=0).count()
    losing_trades = trades.filter(profit_loss__lt=0).count()

    total_profit_loss = trades.aggregate(
        total=Sum('profit_loss')
    )['total'] or 0

    win_rate = 0
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100

    return render(request, 'tracker/monthly_summary.html', {
        'month': month,
        'year': year,
        'trades': trades,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': round(win_rate, 2),
    })