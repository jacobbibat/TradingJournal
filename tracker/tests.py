from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import (
    User,
    Asset,
    Trade,
    BalanceHistory,
    Comment,
    TradeReview,
    Tag,
    TradeScreenshot,
)


class BaseTestCase(TestCase):
    def setUp(self):
        self.trader = User.objects.create_user(
            username='user1',
            email='user1@email.com',
            password='password',
            role='TRADER',
            current_balance=1000
        )

        self.other_trader = User.objects.create_user(
            username='user2',
            email='user2@email.com',
            password='password',
            role='TRADER'
        )

        self.analyst = User.objects.create_user(
            username='analyst1',
            email='analyst@email.com',
            password='password',
            role='ANALYST'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@email.com',
            password='password',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )

        self.asset = Asset.objects.create(
            symbol='GBPUSD',
            name='British Pound / US Dollar',
            description='Forex pair',
            is_active=True
        )

        self.trade = Trade.objects.create(
            trader=self.trader,
            asset=self.asset,
            trade_type='BUY',
            entry_price=100,
            exit_price=110,
            lot_size=1,
            trade_date=timezone.now(),
            notes='Test trade',
            status='CLOSED',
            visibility='PUBLIC'
        )


class ModelTests(BaseTestCase):

    def test_user_created_with_role(self):
        self.assertEqual(self.trader.role, 'TRADER')
        self.assertEqual(str(self.trader), 'user1 (TRADER)')

    def test_asset_created(self):
        self.assertEqual(self.asset.symbol, 'GBPUSD')
        self.assertTrue(self.asset.is_active)
        self.assertEqual(str(self.asset), 'GBPUSD')

    def test_trade_created(self):
        self.assertEqual(self.trade.trader, self.trader)
        self.assertEqual(self.trade.asset, self.asset)
        self.assertEqual(self.trade.trade_type, 'BUY')

    def test_buy_trade_profit_loss_calculation(self):
        self.assertEqual(self.trade.profit_loss, 10)

    def test_sell_trade_profit_loss_calculation(self):
        trade = Trade.objects.create(
            trader=self.trader,
            asset=self.asset,
            trade_type='SELL',
            entry_price=110,
            exit_price=100,
            lot_size=1,
            trade_date=timezone.now(),
            status='CLOSED'
        )

        self.assertEqual(trade.profit_loss, 10)

    def test_balance_history_created(self):
        history = BalanceHistory.objects.create(
            user=self.trader,
            old_balance=1000,
            new_balance=1200,
            change_amount=200,
            change_type='ADJUSTMENT',
            reason='Added funds'
        )

        self.assertEqual(history.user, self.trader)
        self.assertEqual(history.change_amount, 200)

    def test_comment_created(self):
        comment = Comment.objects.create(
            trade=self.trade,
            user=self.trader,
            content='Good trade'
        )

        self.assertEqual(comment.trade, self.trade)
        self.assertEqual(comment.user, self.trader)

    def test_trade_review_created(self):
        review = TradeReview.objects.create(
            trade=self.trade,
            analyst=self.analyst,
            feedback='Good setup',
            review_type='PUBLIC'
        )

        self.assertEqual(review.trade, self.trade)
        self.assertEqual(review.analyst, self.analyst)

    def test_tag_created_and_added_to_trade(self):
        tag = Tag.objects.create(name='Scalping')
        self.trade.tags.add(tag)

        self.assertIn(tag, self.trade.tags.all())


class AuthenticationTests(BaseTestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@email.com',
            'password': 'password'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_login(self):
        login = self.client.login(username='user1', password='password')
        self.assertTrue(login)


class TradeViewTests(BaseTestCase):

    def test_trade_list_requires_login(self):
        response = self.client.get(reverse('trade_list'))
        self.assertEqual(response.status_code, 302)

    def test_trade_list_loads_for_logged_in_user(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('trade_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GBPUSD')

    def test_trade_detail_loads(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('trade_detail', args=[self.trade.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GBPUSD')

    def test_create_trade_page_loads_for_trader(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('trade_create'))

        self.assertEqual(response.status_code, 200)

    def test_trader_can_create_trade(self):
        self.client.login(username='user1', password='password')

        response = self.client.post(reverse('trade_create'), {
            'asset': self.asset.id,
            'trade_type': 'BUY',
            'entry_price': '100',
            'exit_price': '120',
            'lot_size': '1',
            'trade_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'notes': 'Created by test',
            'visibility': 'PRIVATE',
            'status': 'CLOSED',
            'tags': []
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Trade.objects.filter(notes='Created by test').exists())

    def test_trader_can_edit_own_trade(self):
        self.client.login(username='user1', password='password')

        response = self.client.post(reverse('trade_edit', args=[self.trade.id]), {
            'asset': self.asset.id,
            'trade_type': 'BUY',
            'entry_price': '100',
            'exit_price': '130',
            'lot_size': '1',
            'trade_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'notes': 'Updated trade',
            'visibility': 'PRIVATE',
            'status': 'CLOSED',
            'tags': []
        })

        self.assertEqual(response.status_code, 302)
        self.trade.refresh_from_db()
        self.assertEqual(self.trade.notes, 'Updated trade')

    def test_trader_can_delete_own_trade(self):
        self.client.login(username='user1', password='password')

        response = self.client.post(reverse('trade_delete', args=[self.trade.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Trade.objects.filter(id=self.trade.id).exists())

    def test_user_cannot_edit_another_users_trade(self):
        self.client.login(username='user2', password='password')

        response = self.client.get(reverse('trade_edit', args=[self.trade.id]))

        self.assertEqual(response.status_code, 404)


class FilterAndSummaryTests(BaseTestCase):

    def test_filter_by_asset(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('trade_list'), {
            'asset': 'GBPUSD'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GBPUSD')

    def test_filter_by_trade_type(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('trade_list'), {
            'trade_type': 'BUY'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BUY')

    def test_dashboard_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Performance Dashboard')

    def test_monthly_summary_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('monthly_summary'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Summary')


class PublicTradeAndCommentTests(BaseTestCase):

    def test_public_trades_page_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('public_trades'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GBPUSD')

    def test_user_can_comment_on_trade(self):
        self.client.login(username='user1', password='password')

        response = self.client.post(reverse('trade_detail', args=[self.trade.id]), {
            'content': 'Nice trade'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='Nice trade').exists())


class AnalystReviewTests(BaseTestCase):

    def test_analyst_can_open_review_page(self):
        self.client.login(username='analyst1', password='password')

        response = self.client.get(reverse('review_trade', args=[self.trade.id]))

        self.assertEqual(response.status_code, 200)

    def test_analyst_can_review_trade(self):
        self.client.login(username='analyst1', password='password')

        response = self.client.post(reverse('review_trade', args=[self.trade.id]), {
            'feedback': 'Good risk management',
            'review_type': 'PUBLIC'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(TradeReview.objects.filter(feedback='Good risk management').exists())

    def test_trader_cannot_access_review_page(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('review_trade', args=[self.trade.id]))

        self.assertEqual(response.status_code, 302)


class BalanceTests(BaseTestCase):

    def test_update_balance_page_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('update_balance'))

        self.assertEqual(response.status_code, 200)

    def test_user_can_update_balance(self):
        self.client.login(username='user1', password='password')

        response = self.client.post(reverse('update_balance'), {
            'new_balance': '1500',
            'reason': 'Added funds'
        })

        self.assertEqual(response.status_code, 302)

        self.trader.refresh_from_db()
        self.assertEqual(self.trader.current_balance, 1500)

        self.assertTrue(
            BalanceHistory.objects.filter(
                user=self.trader,
                new_balance=1500
            ).exists()
        )

    def test_balance_history_page_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('balance_history'))

        self.assertEqual(response.status_code, 200)


class AssetManagementTests(BaseTestCase):

    def test_admin_can_view_asset_list(self):
        self.client.login(username='admin', password='password')

        response = self.client.get(reverse('asset_list'))

        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_asset(self):
        self.client.login(username='admin', password='password')

        response = self.client.post(reverse('asset_create'), {
            'symbol': 'BTCUSD',
            'name': 'Bitcoin / US Dollar',
            'description': 'Crypto pair',
            'is_active': 'on'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Asset.objects.filter(symbol='BTCUSD').exists())

    def test_admin_can_edit_asset(self):
        self.client.login(username='admin', password='password')

        response = self.client.post(reverse('asset_edit', args=[self.asset.id]), {
            'symbol': 'GBPUSD',
            'name': 'Updated Asset Name',
            'description': 'Updated',
            'is_active': 'on'
        })

        self.assertEqual(response.status_code, 302)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.name, 'Updated Asset Name')

    def test_trader_cannot_access_asset_list(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('asset_list'))

        self.assertEqual(response.status_code, 302)


class ScreenshotTests(BaseTestCase):

    def test_upload_screenshot_page_loads(self):
        self.client.login(username='user1', password='password')

        response = self.client.get(reverse('upload_screenshot', args=[self.trade.id]))

        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_screenshot(self):
        self.client.login(username='user1', password='password')

        image = SimpleUploadedFile(
            name='test_screenshot.png',
            content=b'\x47\x49\x46\x38\x39\x61',
            content_type='image/png'
        )

        screenshot = TradeScreenshot.objects.create(
            trade=self.trade,
            image=image
        )

        response = self.client.post(reverse('delete_screenshot', args=[screenshot.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(TradeScreenshot.objects.filter(id=screenshot.id).exists())