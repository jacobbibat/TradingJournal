from django import forms
from .models import Trade, Comment, TradeReview, BalanceHistory, User, Asset, TradeScreenshot
from django.utils import timezone

#reusable tailwind helper class
def apply_tailwind_classes(fields):
    for field in fields.values():

        if isinstance(field.widget, forms.RadioSelect):
            continue

        field.widget.attrs.update({
            'class': 'w-full border-2 border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-slate-600 focus:ring-2 focus:ring-slate-300'
        })
# Form for creating a Trade with all its fields
class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            'asset',
            'trade_type',
            'entry_price',
            'exit_price',
            'lot_size',
            'trade_date',
            'notes',
            'visibility',
            'status',
            'tags',
        ]

        widgets = {
            'trade_date': forms.DateInput(attrs={
                'type': 'date',
            }),

            'visibility': forms.RadioSelect(),

            'status': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Today's date as default when creating a new trade
        if not self.instance.pk:
            self.fields['trade_date'].initial = timezone.now().date()

        # Normal input styling
        apply_tailwind_classes(self.fields)

        # Better styling for radio buttons
        self.fields['visibility'].widget.attrs.update({
            'class': 'mr-2'
        })

        self.fields['status'].widget.attrs.update({
            'class': 'mr-2'
        })

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)

class TradeReviewForm(forms.ModelForm):
    class Meta:
        model = TradeReview
        fields = ['feedback', 'review_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)

class BalanceUpdateForm(forms.Form):
    new_balance = forms.DecimalField(max_digits=12, decimal_places=2)
    reason = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['symbol', 'name', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)

class TradeScreenshotForm(forms.ModelForm):
    class Meta:
        model = TradeScreenshot
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_tailwind_classes(self.fields)