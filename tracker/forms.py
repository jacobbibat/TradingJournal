from django import forms
from .models import Trade, Comment, TradeReview

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