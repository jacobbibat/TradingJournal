from django.shortcuts import redirect


def trader_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'TRADER':
            return view_func(request, *args, **kwargs)
        return redirect('trade_list')
    return wrapper


def analyst_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'ANALYST':
            return view_func(request, *args, **kwargs)
        return redirect('trade_list')
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            return view_func(request, *args, **kwargs)
        return redirect('trade_list')
    return wrapper