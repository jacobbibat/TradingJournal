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

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'current_balance'),
        }),
    )

    list_display = ('username', 'email', 'role', 'current_balance', 'is_staff')
    list_filter = ('role', 'is_staff')


# Other models
admin.site.register(Asset)
admin.site.register(Trade)
admin.site.register(BalanceHistory)
admin.site.register(Tag)
admin.site.register(TradeScreenshot)
admin.site.register(Comment)
admin.site.register(TradeReview)