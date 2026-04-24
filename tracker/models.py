from django.db import models
from decimal import Decimal
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser): 
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'), # ('value stored in db' , 'human readable label' )
        ('TRADER', 'Trader'),
        ('ANALYST', 'Analyst'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='TRADER'
    )

    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
# Class Asset
class Asset(models.Model):
    symbol = models.CharField(max_length=20, unique=True) #Can only exist once
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.symbol # Returns self.symbol if someone tries print this object
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Trade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    VISIBLITY_CHOICES = [
        ('PRIVATE', 'Private'),
        ('PUBLIC', 'Public')
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed')
    ]

    trader = models.ForeignKey(
        User, # Each Trade belongs to one user
        on_delete=models.CASCADE, # If user is deleted, delete theie trades
        related_name='trades' # Give me all of users trades, rather than trade_set
    )

    asset = models.ForeignKey(
        Asset, # Each trade belongs to ONE asset
        on_delete=models.CASCADE,
        related_name='trades' # Easier to give trades involving this asset
    )

    trade_type = models.CharField(
        max_length=10,
        choices=TRADE_TYPE_CHOICES # buy or sell
    )
    entry_price = models.DecimalField(
        max_digits=12,
        decimal_places = 5        
    )

    exit_price = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        null=True, # Can be empty
        blank=True # In forms, can this field can be optional
    )

    lot_size = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    trade_date = models.DateTimeField() #Gets timestamp

    notes = models.TextField(blank=True) # Can be empty

    profit_loss = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    percentage_return = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )

    visibility = models.CharField(
        max_length=10,
        choices = VISIBLITY_CHOICES,
        default='PRIVATE'
    )

    status = models.CharField(
        max_length=10,
        choices = STATUS_CHOICES,
        default='OPEN'
    )

    tags = models.ManyToManyField(
    Tag,
    blank=True,
    related_name='trades'
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trader.username} - {self.asset.symbol} - {self.trade_type}"
    
    # Logic calculations
    def calculate_profit_loss(self):
        if self.exit_price is None:
            return Decimal('0.00')
        
        if self.trade_type == 'BUY':
            return (self.exit_price - self.entry_price) * self.lot_size
        
        if self.trade_type == 'SELL':
            return (self.entry_price - self.exit_price) * self.lot_size
        
        return Decimal('0.00')
    
    def calculate_percentage_returns(self):
        if self.entry_price == 0:
            return Decimal('0.00')
        
        return (self.profit_loss / (self.entry_price * self.lot_size)) * 100

    def save(self, *args, **kwargs):
        if self.status == 'CLOSED' and self.entry_price is not None: #ONLY RUNS IF TRADE IS CLOSED AND Exit price exists
            self.profit_loss = self.calculate_profit_loss()
            self.percentage_return = self.calculate_percentage_returns()

        super().save(*args, **kwargs) #Django save method

class BalanceHistory(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRADE_RESULT', 'Trade Result'),
    ]

    user = models.ForeignKey(
        User, #Each balance history belongs to one user
        on_delete=models.CASCADE,
        related_name='balance_history'
    )

    related_trade = models.ForeignKey(
        Trade, #One record belongs to one trade
        on_delete=models.SET_NULL, #If trade is deleted, set related trade to NULL
        null=True,
        blank=True, # Can be null and users don't hae to fill in
        related_name='balance_updates'
    )

    old_balance = models.DecimalField(max_digits=12, decimal_places=2)
    new_balance = models.DecimalField(max_digits=12, decimal_places=2)
    change_amount = models.DecimalField(max_digits=12, decimal_places=2)

    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES #EDITABLE
    )

    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} balance change: {self.change_amount}"
    
class TradeScreenshot(models.Model):
    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name='screenshots'
    )

    image = models.ImageField(upload_to='trade_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Screenshot for {self.trade}"
    
class Comment(models.Model):
    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.trade}"
    
class TradeReview(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
    ]

    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    analyst = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trade_reviews'
    )

    feedback = models.TextField()

    review_type = models.CharField(
        max_length=10,
        choices=REVIEW_TYPE_CHOICES,
        default='PRIVATE'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.analyst.username} on {self.trade}"