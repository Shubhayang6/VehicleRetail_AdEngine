import json
import os
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import uuid

@dataclass
class Product:
    """Product in the catalog"""
    product_id: str
    name: str
    category: str
    subcategory: str
    price: float
    description: str
    brand: str
    rating: float
    reviews_count: int
    in_stock: bool
    stock_quantity: int
    image_url: str
    specifications: Dict[str, Any]
    tags: List[str]

@dataclass
class ProductRecommendation:
    """Individual product recommendation"""
    recommendation_id: str
    vehicle_id: str
    product: Product
    relevance_score: float
    recommendation_reason: str
    confidence: float
    price_tier: str
    discount_available: Optional[float]
    urgency_level: str  # low, medium, high
    contextual_factors: List[str]

@dataclass
class AdCampaign:
    """Advertising campaign targeting a user"""
    campaign_id: str
    vehicle_id: str
    campaign_type: str
    title: str
    message: str
    products: List[ProductRecommendation]
    target_audience: str
    delivery_method: str  # infotainment, mobile, email
    display_duration: int  # seconds
    call_to_action: str
    budget_allocated: float
    expected_conversion_rate: float

class ProductCatalogManager:
    """Manages product catalog and inventory"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('ProductCatalog')
        self.products = []
        self.categories = config['recommendation_settings']['product_categories']
        
        # Create products directory
        os.makedirs('products', exist_ok=True)
        
        # Generate product catalog
        self.generate_product_catalog()
    
    def generate_product_catalog(self) -> List[Product]:
        """Generate a comprehensive product catalog"""
        products = []
        product_id_counter = 1
        
        # Define product templates by category
        product_templates = {
            'automotive_parts': [
                {'name': 'Premium Oil Filter', 'subcategory': 'oil_filters', 'price_range': (15, 45), 'brand_options': ['Mobil 1', 'Fram', 'Bosch']},
                {'name': 'High-Flow Air Filter', 'subcategory': 'air_filters', 'price_range': (20, 60), 'brand_options': ['K&N', 'AEM', 'Spectre']},
                {'name': 'Ceramic Brake Pads', 'subcategory': 'brake_pads', 'price_range': (80, 200), 'brand_options': ['Brembo', 'EBC', 'StopTech']},
                {'name': 'All-Season Tire', 'subcategory': 'tires', 'price_range': (120, 300), 'brand_options': ['Michelin', 'Bridgestone', 'Continental']},
                {'name': 'AGM Battery', 'subcategory': 'batteries', 'price_range': (150, 350), 'brand_options': ['Optima', 'Interstate', 'DieHard']}
            ],
            'maintenance_tools': [
                {'name': 'Complete Oil Change Kit', 'subcategory': 'oil_change_kits', 'price_range': (35, 85), 'brand_options': ['Valvoline', 'Castrol', 'Shell']},
                {'name': 'Digital Tire Pressure Gauge', 'subcategory': 'tire_pressure_gauges', 'price_range': (15, 40), 'brand_options': ['AstroAI', 'JACO', 'Rhino USA']},
                {'name': 'OBD2 Scanner', 'subcategory': 'diagnostic_tools', 'price_range': (25, 120), 'brand_options': ['BlueDriver', 'Autel', 'Launch']}
            ],
            'accessories': [
                {'name': 'Car Care Kit', 'subcategory': 'car_care_products', 'price_range': (25, 75), 'brand_options': ['Chemical Guys', 'Meguiars', 'Armor All']},
                {'name': 'Premium Air Freshener', 'subcategory': 'air_fresheners', 'price_range': (8, 25), 'brand_options': ['Little Trees', 'Febreze', 'California Scents']},
                {'name': 'Wireless Phone Mount', 'subcategory': 'phone_mounts', 'price_range': (20, 60), 'brand_options': ['iOttie', 'Belkin', 'ESR']},
                {'name': '4K Dash Camera', 'subcategory': 'dash_cams', 'price_range': (80, 250), 'brand_options': ['Nextbase', 'Garmin', 'VAVA']}
            ],
            'emergency_gear': [
                {'name': 'Portable Jump Starter', 'subcategory': 'jump_starters', 'price_range': (60, 150), 'brand_options': ['NOCO', 'TACKLIFE', 'DBPOWER']},
                {'name': 'Roadside Emergency Kit', 'subcategory': 'emergency_kits', 'price_range': (40, 100), 'brand_options': ['AAA', 'Lifeline', 'Cartman']},
                {'name': 'Auto First Aid Kit', 'subcategory': 'first_aid_kits', 'price_range': (25, 60), 'brand_options': ['Johnson & Johnson', 'First Aid Only', 'Be Smart Get Prepared']}
            ],
            'performance_upgrades': [
                {'name': 'Cold Air Intake System', 'subcategory': 'cold_air_intakes', 'price_range': (200, 500), 'brand_options': ['K&N', 'AEM', 'Injen']},
                {'name': 'Performance Chip', 'subcategory': 'performance_chips', 'price_range': (150, 400), 'brand_options': ['Bully Dog', 'Edge', 'SCT']},
                {'name': 'Cat-Back Exhaust', 'subcategory': 'exhaust_systems', 'price_range': (300, 800), 'brand_options': ['Borla', 'Flowmaster', 'MagnaFlow']}
            ]
        }
        
        # Generate products for each category
        for category, templates in product_templates.items():
            for template in templates:
                for brand in template['brand_options']:
                    # Generate product variations
                    for i in range(2):  # 2 variants per brand
                        product_id = f"PROD_{str(product_id_counter).zfill(4)}"
                        product_id_counter += 1
                        
                        # Random price within range
                        min_price, max_price = template['price_range']
                        price = round(random.uniform(min_price, max_price), 2)
                        
                        # Generate specifications based on category
                        specs = self.generate_specifications(category, template['subcategory'])
                        
                        # Generate tags
                        tags = self.generate_tags(category, template['subcategory'], brand)
                        
                        product = Product(
                            product_id=product_id,
                            name=f"{brand} {template['name']}" + (f" - Model {i+1}" if i > 0 else ""),
                            category=category,
                            subcategory=template['subcategory'],
                            price=price,
                            description=self.generate_description(template['name'], brand, specs),
                            brand=brand,
                            rating=round(random.uniform(3.5, 5.0), 1),
                            reviews_count=random.randint(50, 500),
                            in_stock=random.random() < self.config['product_catalog']['inventory_simulation']['availability_rate'],
                            stock_quantity=random.randint(0, 100),
                            image_url=f"https://images.autoparts.com/{product_id.lower()}.jpg",
                            specifications=specs,
                            tags=tags
                        )
                        
                        products.append(product)
        
        self.products = products
        self.save_catalog_to_file()
        self.logger.info(f"Generated {len(products)} products across {len(product_templates)} categories")
        
        return products
    
    def generate_specifications(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Generate realistic specifications for products"""
        specs = {}
        
        if category == 'automotive_parts':
            if subcategory == 'oil_filters':
                specs = {
                    'filter_type': random.choice(['Spin-on', 'Cartridge']),
                    'filtration_rating': f"{random.randint(15, 25)} microns",
                    'capacity': f"{random.uniform(4.0, 6.0):.1f} quarts"
                }
            elif subcategory == 'tires':
                specs = {
                    'size': random.choice(['215/60R16', '225/65R17', '235/55R18']),
                    'tread_life': f"{random.randint(40, 80)}k miles",
                    'speed_rating': random.choice(['H', 'V', 'W'])
                }
            elif subcategory == 'brake_pads':
                specs = {
                    'material': random.choice(['Ceramic', 'Semi-Metallic', 'Organic']),
                    'noise_level': random.choice(['Low', 'Medium', 'Ultra-Quiet']),
                    'dust_level': random.choice(['Low', 'Medium', 'Dust-Free'])
                }
        
        elif category == 'maintenance_tools':
            if subcategory == 'diagnostic_tools':
                specs = {
                    'compatibility': 'OBD2',
                    'protocols': random.choice(['All Protocols', 'CAN, ISO, KWP']),
                    'display': random.choice(['LCD', 'Color Screen', 'Mobile App'])
                }
        
        elif category == 'accessories':
            if subcategory == 'dash_cams':
                specs = {
                    'resolution': random.choice(['1080p', '4K', '2K']),
                    'field_of_view': f"{random.randint(140, 170)}°",
                    'storage': random.choice(['32GB', '64GB', '128GB'])
                }
        
        # Add common specs
        specs.update({
            'warranty': f"{random.randint(1, 5)} years",
            'weight': f"{random.uniform(0.5, 5.0):.1f} lbs"
        })
        
        return specs
    
    def generate_tags(self, category: str, subcategory: str, brand: str) -> List[str]:
        """Generate relevant tags for products"""
        tags = [category, subcategory, brand.lower()]
        
        # Add category-specific tags
        if category == 'automotive_parts':
            tags.extend(['maintenance', 'replacement', 'OEM'])
        elif category == 'performance_upgrades':
            tags.extend(['performance', 'upgrade', 'tuning'])
        elif category == 'emergency_gear':
            tags.extend(['safety', 'emergency', 'roadside'])
        
        # Add quality indicators
        tags.extend(['quality', 'reliable', 'tested'])
        
        return tags
    
    def generate_description(self, name: str, brand: str, specs: Dict) -> str:
        """Generate product description"""
        base_desc = f"High-quality {name.lower()} from {brand}. "
        
        # Add key specifications
        if 'material' in specs:
            base_desc += f"Features {specs['material'].lower()} construction. "
        if 'warranty' in specs:
            base_desc += f"Includes {specs['warranty']} warranty. "
        
        base_desc += "Professional installation recommended. Compatible with most vehicle models."
        
        return base_desc
    
    def save_catalog_to_file(self):
        """Save product catalog to JSON file"""
        catalog_data = {
            'generated_at': datetime.now().isoformat(),
            'total_products': len(self.products),
            'categories': list(self.categories.keys()),
            'products': [asdict(product) for product in self.products]
        }
        
        with open('products/product_catalog.json', 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        self.logger.info("Product catalog saved to products/product_catalog.json")
    
    def get_products_by_category(self, category: str, subcategory: str = None) -> List[Product]:
        """Get products filtered by category"""
        filtered = [p for p in self.products if p.category == category]
        
        if subcategory:
            filtered = [p for p in filtered if p.subcategory == subcategory]
        
        return filtered
    
    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Get products within price range"""
        return [p for p in self.products if min_price <= p.price <= max_price]
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name, description, or tags"""
        query_lower = query.lower()
        
        results = []
        for product in self.products:
            if (query_lower in product.name.lower() or 
                query_lower in product.description.lower() or 
                any(query_lower in tag for tag in product.tags)):
                results.append(product)
        
        return results

class RecommendationEngine:
    """Core recommendation engine using collaborative and content-based filtering"""
    
    def __init__(self, config: Dict, catalog_manager: ProductCatalogManager):
        self.config = config
        self.catalog = catalog_manager
        self.logger = logging.getLogger('RecommendationEngine')
        
        # Recommendation algorithms
        self.algorithms = config['recommendation_settings']['recommendation_algorithms']
        self.targeting = config['recommendation_settings']['targeting_criteria']
        self.limits = config['personalization']['recommendation_limits']
    
    def analyze_user_behavior(self, vehicle_data: Dict) -> Dict[str, float]:
        """Analyze user behavior from vehicle data"""
        behavior_profile = vehicle_data.get('behavior_profile', {})
        
        analysis = {
            'aggressiveness': behavior_profile.get('driving_aggressiveness', 0.5),
            'eco_consciousness': behavior_profile.get('eco_driving_score', 0.5),
            'maintenance_awareness': 1.0 if behavior_profile.get('maintenance_needs', False) else 0.7,
            'performance_orientation': min(1.0, behavior_profile.get('driving_aggressiveness', 0.3) * 1.5),
            'safety_consciousness': 1 - behavior_profile.get('driving_aggressiveness', 0.5),
            'cost_sensitivity': 1 - (vehicle_data.get('vehicle_profile', {}).get('health_score', 0.8))
        }
        
        return analysis
    
    def analyze_context(self, vehicle_data: Dict) -> Dict[str, Any]:
        """Analyze contextual factors"""
        context = vehicle_data.get('context', {})
        
        analysis = {
            'location_type': self.classify_location(context),
            'weather_impact': self.analyze_weather_impact(context.get('weather', 'clear')),
            'terrain_demands': self.analyze_terrain_demands(context.get('terrain', 'city')),
            'seasonal_needs': self.get_seasonal_recommendations(),
            'urgency_level': self.determine_urgency(vehicle_data)
        }
        
        return analysis
    
    def classify_location(self, context: Dict) -> str:
        """Classify driving location type"""
        # Mock classification based on speed and context
        speed = context.get('speed', 50)
        terrain = context.get('terrain', 'city')
        
        if terrain == 'highway' or speed > 80:
            return 'highway'
        elif terrain == 'city' or speed < 40:
            return 'urban'
        else:
            return 'suburban'
    
    def analyze_weather_impact(self, weather: str) -> List[str]:
        """Analyze weather impact on product needs"""
        weather_recommendations = {
            'rain': ['tire_pressure', 'windshield_wipers', 'brake_maintenance'],
            'snow': ['winter_tires', 'antifreeze', 'emergency_kit'],
            'fog': ['lighting_upgrade', 'visibility_products'],
            'clear': ['general_maintenance', 'performance_upgrade']
        }
        
        return weather_recommendations.get(weather, weather_recommendations['clear'])
    
    def analyze_terrain_demands(self, terrain: str) -> List[str]:
        """Analyze terrain impact on vehicle needs"""
        terrain_recommendations = {
            'highway': ['performance_upgrade', 'tire_maintenance', 'fuel_efficiency'],
            'city': ['brake_maintenance', 'air_filter', 'stop_start_battery'],
            'mixed': ['all_season_tires', 'suspension', 'general_maintenance']
        }
        
        return terrain_recommendations.get(terrain, terrain_recommendations['mixed'])
    
    def get_seasonal_recommendations(self) -> List[str]:
        """Get seasonal product recommendations"""
        # Simple seasonal logic based on current month
        month = datetime.now().month
        
        if month in [12, 1, 2]:  # Winter
            return self.config['marketing_campaigns']['seasonal']['winter']
        elif month in [3, 4, 5]:  # Spring
            return self.config['marketing_campaigns']['seasonal']['spring']
        elif month in [6, 7, 8]:  # Summer
            return self.config['marketing_campaigns']['seasonal']['summer']
        else:  # Fall
            return self.config['marketing_campaigns']['seasonal']['fall']
    
    def determine_urgency(self, vehicle_data: Dict) -> str:
        """Determine purchase urgency"""
        behavior_profile = vehicle_data.get('behavior_profile', {})
        vehicle_profile = vehicle_data.get('vehicle_profile', {})
        
        if behavior_profile.get('maintenance_needs', False):
            return 'high'
        elif vehicle_profile.get('health_score', 1.0) < 0.6:
            return 'medium'
        else:
            return 'low'
    
    def calculate_behavioral_relevance(self, product: Product, behavior_analysis: Dict) -> float:
        """Calculate relevance based on behavioral factors"""
        relevance = 0.0
        
        # Map product categories to behavioral traits
        if product.category == 'performance_upgrades':
            relevance += behavior_analysis['performance_orientation'] * 0.8
            relevance += (1 - behavior_analysis['cost_sensitivity']) * 0.2
        
        elif product.category == 'automotive_parts':
            relevance += behavior_analysis['maintenance_awareness'] * 0.6
            relevance += behavior_analysis['safety_consciousness'] * 0.4
        
        elif product.category == 'emergency_gear':
            relevance += behavior_analysis['safety_consciousness'] * 0.9
            relevance += behavior_analysis['cost_sensitivity'] * 0.1
        
        elif product.category == 'accessories':
            if 'eco' in product.tags or 'efficiency' in product.tags:
                relevance += behavior_analysis['eco_consciousness'] * 0.7
            relevance += (1 - behavior_analysis['cost_sensitivity']) * 0.3
        
        return min(relevance, 1.0)
    
    def calculate_contextual_relevance(self, product: Product, context_analysis: Dict) -> float:
        """Calculate relevance based on contextual factors"""
        relevance = 0.0
        
        # Seasonal relevance
        seasonal_needs = context_analysis['seasonal_needs']
        if any(need in product.tags or need in product.subcategory for need in seasonal_needs):
            relevance += 0.4
        
        # Weather relevance
        weather_needs = context_analysis['weather_impact']
        if any(need in product.tags or need in product.subcategory for need in weather_needs):
            relevance += 0.3
        
        # Terrain relevance
        terrain_needs = context_analysis['terrain_demands']
        if any(need in product.tags or need in product.subcategory for need in terrain_needs):
            relevance += 0.3
        
        return min(relevance, 1.0)
    
    def calculate_health_based_relevance(self, product: Product, vehicle_data: Dict) -> float:
        """Calculate relevance based on vehicle health"""
        vehicle_profile = vehicle_data.get('vehicle_profile', {})
        behavior_profile = vehicle_data.get('behavior_profile', {})
        
        health_score = vehicle_profile.get('health_score', 0.8)
        maintenance_needs = behavior_profile.get('maintenance_needs', False)
        
        relevance = 0.0
        
        # High relevance for maintenance products when health is low
        if health_score < 0.6 and product.category == 'automotive_parts':
            relevance += 0.8
        
        # High relevance for emergency gear when health is questionable
        if health_score < 0.7 and product.category == 'emergency_gear':
            relevance += 0.6
        
        # Direct maintenance needs
        if maintenance_needs and product.category in ['automotive_parts', 'maintenance_tools']:
            relevance += 0.9
        
        return min(relevance, 1.0)
    
    def generate_recommendations(self, vehicle_data: Dict) -> List[ProductRecommendation]:
        """Generate personalized product recommendations"""
        vehicle_id = vehicle_data.get('vehicle_id', 'unknown')
        
        # Analyze user profile
        behavior_analysis = self.analyze_user_behavior(vehicle_data)
        context_analysis = self.analyze_context(vehicle_data)
        
        # Get candidate products (filter by availability)
        available_products = [p for p in self.catalog.products if p.in_stock]
        
        # Calculate relevance scores for all products
        scored_products = []
        
        for product in available_products:
            # Calculate component scores
            behavioral_score = self.calculate_behavioral_relevance(product, behavior_analysis)
            contextual_score = self.calculate_contextual_relevance(product, context_analysis)
            health_score = self.calculate_health_based_relevance(product, vehicle_data)
            
            # Weighted total score
            weights = self.algorithms
            total_score = (
                behavioral_score * weights['behavioral_filtering']['weight'] +
                contextual_score * weights['contextual_filtering']['weight'] +
                health_score * weights['health_based_filtering']['weight']
            )
            
            # Only include products above relevance threshold
            if total_score >= self.limits['relevance_threshold']:
                scored_products.append((product, total_score, {
                    'behavioral': behavioral_score,
                    'contextual': contextual_score,
                    'health': health_score
                }))
        
        # Sort by relevance score
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Limit number of recommendations
        max_recommendations = self.limits['max_recommendations_per_session']
        top_products = scored_products[:max_recommendations]
        
        # Generate recommendation objects
        recommendations = []
        
        for i, (product, score, component_scores) in enumerate(top_products):
            recommendation_id = f"REC_{vehicle_id}_{str(uuid.uuid4())[:8]}"
            
            # Generate recommendation reason
            reason = self.generate_recommendation_reason(product, component_scores, context_analysis)
            
            # Determine urgency
            urgency = context_analysis['urgency_level']
            
            # Calculate discount
            discount = self.calculate_discount(product, behavior_analysis, i)
            
            # Determine price tier
            price_tier = self.determine_price_tier(product.price)
            
            # Generate contextual factors
            contextual_factors = self.extract_contextual_factors(context_analysis, component_scores)
            
            recommendation = ProductRecommendation(
                recommendation_id=recommendation_id,
                vehicle_id=vehicle_id,
                product=product,
                relevance_score=score,
                recommendation_reason=reason,
                confidence=min(score * 1.2, 1.0),  # Boost confidence slightly
                price_tier=price_tier,
                discount_available=discount,
                urgency_level=urgency,
                contextual_factors=contextual_factors
            )
            
            recommendations.append(recommendation)
        
        self.logger.info(f"Generated {len(recommendations)} recommendations for {vehicle_id}")
        return recommendations
    
    def generate_recommendation_reason(self, product: Product, scores: Dict, context: Dict) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        # Find the highest scoring component
        max_component = max(scores.items(), key=lambda x: x[1])
        component, score = max_component
        
        if component == 'behavioral' and score > 0.6:
            if product.category == 'performance_upgrades':
                reasons.append("Based on your performance-oriented driving style")
            elif product.category == 'emergency_gear':
                reasons.append("Recommended for safety-conscious drivers")
        
        elif component == 'contextual' and score > 0.6:
            if context['urgency_level'] == 'high':
                reasons.append("Urgent need detected based on current conditions")
            else:
                reasons.append("Perfect for current weather and driving conditions")
        
        elif component == 'health' and score > 0.6:
            reasons.append("Recommended based on your vehicle's maintenance needs")
        
        # Add seasonal/contextual reasons
        if any(season in product.tags for season in ['winter', 'summer', 'spring', 'fall']):
            reasons.append("Seasonal recommendation")
        
        # Default reason
        if not reasons:
            reasons.append("Highly rated product matching your profile")
        
        return ". ".join(reasons)
    
    def calculate_discount(self, product: Product, behavior_analysis: Dict, position: int) -> Optional[float]:
        """Calculate available discount"""
        discounts = self.config['marketing_campaigns']['promotional']
        
        # New customer discount (simulate)
        if random.random() < 0.3:  # 30% chance
            return discounts['new_customer']
        
        # Loyalty discount for maintenance-aware users
        if behavior_analysis['maintenance_awareness'] > 0.8:
            return discounts['loyalty_discount']
        
        # Top recommendation gets bulk discount
        if position == 0 and random.random() < 0.2:
            return discounts['bulk_purchase']
        
        return None
    
    def determine_price_tier(self, price: float) -> str:
        """Determine price tier"""
        tiers = self.config['product_catalog']['pricing_tiers']
        
        for tier, range_dict in tiers.items():
            if range_dict['min'] <= price <= range_dict['max']:
                return tier
        
        return 'premium' if price > 500 else 'budget'
    
    def extract_contextual_factors(self, context_analysis: Dict, scores: Dict) -> List[str]:
        """Extract key contextual factors"""
        factors = []
        
        factors.append(f"Location: {context_analysis['location_type']}")
        factors.append(f"Urgency: {context_analysis['urgency_level']}")
        
        if scores['contextual'] > 0.5:
            factors.extend(context_analysis['weather_impact'][:2])
        
        if scores['health'] > 0.5:
            factors.append("Vehicle health consideration")
        
        return factors

if __name__ == "__main__":
    # Test the product catalog and recommendation engine
    print("Initializing Ad & Recommendation Engine...")
    
    # Load configuration
    with open('ad_engine_config.json', 'r') as f:
        config = json.load(f)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize components
    catalog_manager = ProductCatalogManager(config)
    recommendation_engine = RecommendationEngine(config, catalog_manager)
    
    print(f"\nProduct Catalog Generated:")
    print(f"  Total Products: {len(catalog_manager.products)}")
    print(f"  Categories: {len(catalog_manager.categories)}")
    
    # Test with sample vehicle data
    sample_vehicle_data = {
        'vehicle_id': 'VEH_TEST',
        'behavior_profile': {
            'driving_aggressiveness': 0.7,
            'eco_driving_score': 0.4,
            'maintenance_needs': True
        },
        'context': {
            'location': [40.7128, -74.0060],
            'weather': 'snow',
            'terrain': 'city',
            'speed': 35
        },
        'vehicle_profile': {
            'mileage': 95000,
            'health_score': 0.65
        }
    }
    
    print("\nGenerating test recommendations...")
    recommendations = recommendation_engine.generate_recommendations(sample_vehicle_data)
    
    print(f"\nGenerated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec.product.name} (${rec.product.price})")
        print(f"     Relevance: {rec.relevance_score:.3f} | {rec.recommendation_reason}")
        if rec.discount_available:
            print(f"     Discount: {rec.discount_available*100:.0f}% off")
        print()
    
    print("Ad & Recommendation Engine initialization complete!")
