import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import random

@dataclass
class ShoppingCart:
    """Shopping cart for vehicle-specific purchases"""
    cart_id: str
    vehicle_id: str
    items: List[Dict]
    subtotal: float
    tax: float
    shipping: float
    total: float
    currency: str
    created_at: str
    updated_at: str

@dataclass
class Order:
    """E-commerce order"""
    order_id: str
    vehicle_id: str
    customer_info: Dict
    items: List[Dict]
    subtotal: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    total_amount: float
    currency: str
    payment_method: str
    payment_status: str
    order_status: str
    shipping_address: Dict
    estimated_delivery: str
    tracking_number: Optional[str]
    created_at: str

@dataclass
class PaymentResult:
    """Payment processing result"""
    payment_id: str
    order_id: str
    amount: float
    currency: str
    payment_method: str
    status: str  # success, failed, pending
    transaction_id: str
    gateway_response: Dict
    processed_at: str

class EcommerceAPI:
    """
    Local E-commerce API that integrates with the Ad Engine
    to enable product purchases from personalized advertisements
    """
    
    def __init__(self, config_file='../Ad_Engine/ad_engine_config.json'):
        """Initialize E-commerce API"""
        self.config = self.load_config(config_file)
        
        # Create data directories
        for dir_path in ['orders', 'payments', 'carts', 'analytics']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('EcommerceAPI')
        
        # Business settings
        self.tax_rate = 0.08  # 8% sales tax
        self.shipping_rates = {
            'standard': 9.99,
            'expedited': 19.99,
            'overnight': 39.99,
            'free_threshold': 75.00  # Free shipping over $75
        }
        
        # Payment gateway simulation
        self.payment_success_rate = 0.92  # 92% success rate
        
        # Statistics
        self.ecommerce_stats = {
            'carts_created': 0,
            'orders_placed': 0,
            'orders_completed': 0,
            'total_revenue': 0.0,
            'conversion_rate': 0.0
        }
    
    def load_config(self, config_file):
        """Load configuration"""
        default_config = {
            'ad_data_path': '../Ad_Engine/ads/',
            'recommendation_data_path': '../Ad_Engine/recommendations/'
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def load_ad_campaigns(self) -> List[Dict]:
        """Load personalized ads to enable purchase flows"""
        ads_path = self.config['ad_data_path']
        
        if not os.path.exists(ads_path):
            self.logger.warning(f"Ads directory not found: {ads_path}")
            return []
        
        # Find latest ads file
        ad_files = [f for f in os.listdir(ads_path) if f.startswith('personalized_ads_')]
        
        if not ad_files:
            self.logger.warning("No ad files found")
            return []
        
        latest_file = sorted(ad_files)[-1]
        file_path = os.path.join(ads_path, latest_file)
        
        ads = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        ads.append(json.loads(line.strip()))
            
            self.logger.info(f"Loaded {len(ads)} ad campaigns from {latest_file}")
            return ads
            
        except Exception as e:
            self.logger.error(f"Error loading ads: {e}")
            return []
    
    def simulate_customer_click(self, ad: Dict) -> bool:
        """Simulate customer clicking on an ad"""
        expected_ctr = ad.get('expected_ctr', 0.05)
        return random.random() < expected_ctr
    
    def generate_customer_info(self, vehicle_id: str, segment: str) -> Dict:
        """Generate mock customer information"""
        customer_names = {
            'performance_enthusiast': ['Alex Rodriguez', 'Mike Johnson', 'Sarah Williams'],
            'eco_driver': ['Jennifer Green', 'David Park', 'Emily Chen'],
            'safety_conscious': ['Robert Smith', 'Mary Johnson', 'James Wilson'],
            'convenience_seeker': ['Lisa Anderson', 'Tom Brown', 'Anna Davis']
        }
        
        names = customer_names.get(segment, ['John Doe'])
        name = random.choice(names)
        
        return {
            'customer_id': f"CUST_{vehicle_id}",
            'name': name,
            'email': f"{name.lower().replace(' ', '.')}@email.com",
            'phone': f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'loyalty_member': random.choice([True, False]),
            'previous_orders': random.randint(0, 5)
        }
    
    def generate_shipping_address(self) -> Dict:
        """Generate mock shipping address"""
        addresses = [
            {
                'street': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'country': 'USA'
            },
            {
                'street': '456 Oak Avenue',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90210',
                'country': 'USA'
            },
            {
                'street': '789 Pine Road',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'country': 'USA'
            }
        ]
        
        return random.choice(addresses)
    
    def create_shopping_cart(self, vehicle_id: str, products: List[Dict]) -> ShoppingCart:
        """Create shopping cart from ad products"""
        cart_id = f"CART_{vehicle_id}_{str(uuid.uuid4())[:8]}"
        
        # Convert products to cart items
        cart_items = []
        subtotal = 0.0
        
        for product_rec in products:
            product = product_rec['product']
            
            # Apply discount if available
            original_price = product['price']
            discount = product_rec.get('discount_available', 0)
            final_price = original_price * (1 - discount)
            
            item = {
                'product_id': product['product_id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'original_price': original_price,
                'discount_percent': discount * 100 if discount else 0,
                'final_price': final_price,
                'quantity': 1,
                'line_total': final_price
            }
            
            cart_items.append(item)
            subtotal += final_price
        
        # Calculate tax and shipping
        tax = subtotal * self.tax_rate
        
        # Free shipping over threshold
        if subtotal >= self.shipping_rates['free_threshold']:
            shipping = 0.0
        else:
            shipping = self.shipping_rates['standard']
        
        total = subtotal + tax + shipping
        
        cart = ShoppingCart(
            cart_id=cart_id,
            vehicle_id=vehicle_id,
            items=cart_items,
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            shipping=round(shipping, 2),
            total=round(total, 2),
            currency='USD',
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.ecommerce_stats['carts_created'] += 1
        return cart
    
    def simulate_checkout_process(self, cart: ShoppingCart, customer_info: Dict) -> Tuple[Order, bool]:
        """Simulate customer checkout process"""
        order_id = f"ORD_{cart.vehicle_id}_{str(uuid.uuid4())[:8]}"
        
        # Simulate checkout completion rate (85%)
        checkout_completed = random.random() < 0.85
        
        if not checkout_completed:
            self.logger.info(f"Cart {cart.cart_id} abandoned during checkout")
            return None, False
        
        # Generate shipping address
        shipping_address = self.generate_shipping_address()
        
        # Calculate delivery estimate
        estimated_delivery = (datetime.now() + timedelta(days=random.randint(3, 7))).strftime('%Y-%m-%d')
        
        # Select payment method
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay']
        payment_method = random.choice(payment_methods)
        
        order = Order(
            order_id=order_id,
            vehicle_id=cart.vehicle_id,
            customer_info=customer_info,
            items=cart.items,
            subtotal=cart.subtotal,
            tax_amount=cart.tax,
            shipping_amount=cart.shipping,
            discount_amount=sum(item['original_price'] - item['final_price'] for item in cart.items),
            total_amount=cart.total,
            currency=cart.currency,
            payment_method=payment_method,
            payment_status='pending',
            order_status='processing',
            shipping_address=shipping_address,
            estimated_delivery=estimated_delivery,
            tracking_number=None,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.ecommerce_stats['orders_placed'] += 1
        return order, True
    
    def process_payment(self, order: Order) -> PaymentResult:
        """Simulate payment processing"""
        payment_id = f"PAY_{order.order_id}_{str(uuid.uuid4())[:8]}"
        transaction_id = f"TXN_{random.randint(1000000, 9999999)}"
        
        # Simulate payment success/failure
        payment_successful = random.random() < self.payment_success_rate
        
        if payment_successful:
            status = 'success'
            gateway_response = {
                'response_code': '00',
                'message': 'Transaction approved',
                'authorization_code': f"AUTH{random.randint(100000, 999999)}",
                'gateway': 'MockPaymentGateway'
            }
            
            # Update order status
            order.payment_status = 'completed'
            order.order_status = 'confirmed'
            order.tracking_number = f"TRACK{random.randint(1000000000, 9999999999)}"
            
            # Update revenue
            self.ecommerce_stats['total_revenue'] += order.total_amount
            self.ecommerce_stats['orders_completed'] += 1
            
        else:
            status = 'failed'
            gateway_response = {
                'response_code': '05',
                'message': 'Transaction declined',
                'error_reason': random.choice(['Insufficient funds', 'Invalid card', 'Card expired']),
                'gateway': 'MockPaymentGateway'
            }
            
            order.payment_status = 'failed'
            order.order_status = 'cancelled'
        
        payment_result = PaymentResult(
            payment_id=payment_id,
            order_id=order.order_id,
            amount=order.total_amount,
            currency=order.currency,
            payment_method=order.payment_method,
            status=status,
            transaction_id=transaction_id,
            gateway_response=gateway_response,
            processed_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return payment_result
    
    def generate_order_confirmation_email(self, order: Order, payment: PaymentResult) -> Dict:
        """Generate order confirmation email data"""
        if payment.status != 'success':
            return None
        
        email_data = {
            'email_id': f"EMAIL_{order.order_id}",
            'to': order.customer_info['email'],
            'subject': f"Order Confirmation - {order.order_id}",
            'template': 'order_confirmation',
            'data': {
                'customer_name': order.customer_info['name'],
                'order_id': order.order_id,
                'order_total': order.total_amount,
                'items': order.items,
                'tracking_number': order.tracking_number,
                'estimated_delivery': order.estimated_delivery,
                'shipping_address': order.shipping_address
            },
            'scheduled_send': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return email_data
    
    def simulate_ecommerce_flow(self):
        """Simulate complete e-commerce flow from ads to orders"""
        self.logger.info("Starting e-commerce simulation...")
        
        # Load ad campaigns
        ads = self.load_ad_campaigns()
        
        if not ads:
            self.logger.warning("No ads found for e-commerce simulation")
            return
        
        carts = []
        orders = []
        payments = []
        emails = []
        
        # Process each ad campaign
        for ad in ads:
            try:
                vehicle_id = ad['vehicle_id']
                segment = ad['target_segment']
                featured_products = ad.get('featured_products', [])
                
                # Simulate customer clicking on ad
                if self.simulate_customer_click(ad):
                    self.logger.info(f"Customer clicked on ad for {vehicle_id}")
                    
                    # Create shopping cart
                    cart = self.create_shopping_cart(vehicle_id, featured_products)
                    carts.append(cart)
                    
                    # Generate customer info
                    customer_info = self.generate_customer_info(vehicle_id, segment)
                    
                    # Simulate checkout
                    order, checkout_success = self.simulate_checkout_process(cart, customer_info)
                    
                    if checkout_success and order:
                        orders.append(order)
                        
                        # Process payment
                        payment_result = self.process_payment(order)
                        payments.append(payment_result)
                        
                        # Generate email if successful
                        if payment_result.status == 'success':
                            email_data = self.generate_order_confirmation_email(order, payment_result)
                            if email_data:
                                emails.append(email_data)
                        
                        self.logger.info(f"Order {order.order_id}: {payment_result.status} - ${order.total_amount}")
                
            except Exception as e:
                self.logger.error(f"Error processing ad for {ad.get('vehicle_id', 'unknown')}: {e}")
        
        # Calculate conversion rate
        if len(ads) > 0:
            self.ecommerce_stats['conversion_rate'] = len(orders) / len(ads)
        
        # Save results
        self.save_carts(carts)
        self.save_orders(orders)
        self.save_payments(payments)
        self.save_emails(emails)
        self.generate_ecommerce_analytics()
        
        self.logger.info(f"E-commerce simulation complete: {len(orders)} orders from {len(ads)} ads")
    
    def save_carts(self, carts: List[ShoppingCart]):
        """Save shopping carts"""
        if not carts:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"carts/shopping_carts_{timestamp}.jsonl"
        
        with open(output_file, 'w') as f:
            for cart in carts:
                f.write(json.dumps(asdict(cart)) + '\n')
        
        self.logger.info(f"Saved {len(carts)} shopping carts to {output_file}")
    
    def save_orders(self, orders: List[Order]):
        """Save orders"""
        if not orders:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"orders/orders_{timestamp}.jsonl"
        
        with open(output_file, 'w') as f:
            for order in orders:
                f.write(json.dumps(asdict(order)) + '\n')
        
        self.logger.info(f"Saved {len(orders)} orders to {output_file}")
    
    def save_payments(self, payments: List[PaymentResult]):
        """Save payment results"""
        if not payments:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"payments/payments_{timestamp}.jsonl"
        
        with open(output_file, 'w') as f:
            for payment in payments:
                f.write(json.dumps(asdict(payment)) + '\n')
        
        self.logger.info(f"Saved {len(payments)} payments to {output_file}")
    
    def save_emails(self, emails: List[Dict]):
        """Save email notifications"""
        if not emails:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"emails_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(emails, f, indent=2)
        
        self.logger.info(f"Saved {len(emails)} email notifications to {output_file}")
    
    def generate_ecommerce_analytics(self):
        """Generate comprehensive e-commerce analytics"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        analytics = {
            'analytics_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'performance_metrics': {
                'total_carts_created': self.ecommerce_stats['carts_created'],
                'total_orders_placed': self.ecommerce_stats['orders_placed'],
                'total_orders_completed': self.ecommerce_stats['orders_completed'],
                'conversion_rate': round(self.ecommerce_stats['conversion_rate'] * 100, 2),
                'total_revenue': round(self.ecommerce_stats['total_revenue'], 2),
                'average_order_value': round(
                    self.ecommerce_stats['total_revenue'] / max(self.ecommerce_stats['orders_completed'], 1), 2
                )
            },
            'business_insights': {
                'cart_abandonment_rate': round(
                    (self.ecommerce_stats['carts_created'] - self.ecommerce_stats['orders_placed']) / 
                    max(self.ecommerce_stats['carts_created'], 1) * 100, 2
                ),
                'payment_success_rate': round(
                    self.ecommerce_stats['orders_completed'] / 
                    max(self.ecommerce_stats['orders_placed'], 1) * 100, 2
                ),
                'estimated_monthly_revenue': round(self.ecommerce_stats['total_revenue'] * 30, 2)
            }
        }
        
        output_file = f"analytics/ecommerce_analytics_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(analytics, f, indent=2)
        
        self.logger.info(f"Generated e-commerce analytics: {output_file}")

if __name__ == "__main__":
    # Run E-commerce simulation
    ecommerce_api = EcommerceAPI()
    
    try:
        print("Starting E-commerce API Simulation...")
        print("This simulates the complete purchase flow:")
        print("  1. Load personalized ads from Ad Engine")
        print("  2. Simulate customer clicks and cart creation")
        print("  3. Process checkout and payment")
        print("  4. Generate order confirmations and emails")
        print()
        
        # Run simulation
        ecommerce_api.simulate_ecommerce_flow()
        
        print("\n=== E-COMMERCE RESULTS ===")
        stats = ecommerce_api.ecommerce_stats
        
        print(f"Shopping Carts Created: {stats['carts_created']}")
        print(f"Orders Placed: {stats['orders_placed']}")
        print(f"Orders Completed: {stats['orders_completed']}")
        print(f"Conversion Rate: {stats['conversion_rate']*100:.1f}%")
        print(f"Total Revenue: ${stats['total_revenue']:.2f}")
        
        if stats['orders_completed'] > 0:
            avg_order = stats['total_revenue'] / stats['orders_completed']
            print(f"Average Order Value: ${avg_order:.2f}")
        
        print(f"\nGenerated files:")
        print(f"  - carts/: Shopping cart data")
        print(f"  - orders/: Order details")
        print(f"  - payments/: Payment transactions")
        print(f"  - analytics/: Business analytics")
        
    except Exception as e:
        print(f"E-commerce simulation failed: {e}")
        import traceback
        traceback.print_exc()
