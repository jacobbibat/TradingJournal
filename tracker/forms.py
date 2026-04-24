from django import forms
from .models import Trade, Comment, TradeReview, BalanceHistory

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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  

class TradeReviewForm(forms.ModelForm):
    class Meta:
        model = TradeReview
        fields = ['feedback', 'review_type']

class BalanceUpdateForm(forms.Form):
    new_balance = forms.DecimalField(max_digits=12, decimal_places=2)
    reason = forms.CharField(widget=forms.Textarea, required=False)