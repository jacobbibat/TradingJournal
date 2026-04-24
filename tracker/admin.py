from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Asset,
    Trade,
    BalanceHistory,
    Tag,
    TradeScreenshot,
    Comment,
    TradeReview
)

admin.site.register(User, UserAdmin)
admin.site.register(Asset)
admin.site.register(Trade)
admin.site.register(BalanceHistory)
admin.site.register(Tag)
admin.site.register(TradeScreenshot)
admin.site.register(Comment)
admin.site.register(TradeReview)