import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid

from recommendation_engine import ProductCatalogManager, RecommendationEngine, ProductRecommendation, AdCampaign

@dataclass
class PersonalizedAd:
    """Personalized advertisement for a vehicle/user"""
    ad_id: str
    vehicle_id: str
    timestamp: str
    
    # Ad content
    headline: str
    message: str
    call_to_action: str
    
    # Product recommendations
    featured_products: List[ProductRecommendation]
    
    # Targeting info
    target_segment: str
    relevance_score: float
    
    # Display specifications
    display_format: str  # banner, popup, native, video
    display_duration: int  # seconds
    display_locations: List[str]  # infotainment, mobile, web
    
    # Campaign details
    campaign_type: str
    budget_allocation: float
    expected_ctr: float  # click-through rate
    
    # Personalization
    user_preferences: Dict[str, any]
    contextual_triggers: List[str]

class AdEngineService:
    """
    Main Ad Engine Service that processes Branch 3 data from Data Processing Service
    and generates personalized advertisements and product recommendations
    """
    
    def __init__(self, config_file='ad_engine_config.json'):
        """Initialize Ad Engine Service"""
        self.config = self.load_config(config_file)
        
        # Create output directories
        for dir_path in ['recommendations', 'campaigns', 'analytics', 'ads']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('AdEngineService')
        
        # Initialize recommendation engine
        self.catalog_manager = ProductCatalogManager(self.config)
        self.recommendation_engine = RecommendationEngine(self.config, self.catalog_manager)
        
        # User segmentation
        self.user_segments = self.config['personalization']['user_segments']
        
        # Statistics tracking
        self.ad_stats = {
            'vehicles_processed': 0,
            'recommendations_generated': 0,
            'ads_created': 0,
            'campaigns_launched': 0,
            'total_budget_allocated': 0.0
        }
    
    def load_config(self, config_file):
        """Load configuration with defaults"""
        default_config = {
            'data_sources': {
                'input_path': '../Data_Processing/output/ad_engine/ad_input_data.jsonl'
            },
            'personalization': {
                'user_segments': {
                    'eco_driver': ['fuel_efficiency', 'environmental', 'cost_savings'],
                    'performance_enthusiast': ['speed', 'power', 'upgrades'],
                    'safety_conscious': ['safety', 'reliability', 'emergency_gear'],
                    'convenience_seeker': ['automation', 'comfort', 'time_saving']
                }
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def load_ad_input_data(self) -> List[Dict]:
        """Load data from Branch 3 (Ad Engine) of Data Processing Service"""
        input_path = self.config['data_sources']['input_path']
        
        if not os.path.exists(input_path):
            self.logger.warning(f"Ad input data not found: {input_path}")
            return []
        
        ad_data = []
        try:
            with open(input_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        ad_data.append(data)
            
            self.logger.info(f"Loaded {len(ad_data)} vehicles from Ad Engine branch")
            return ad_data
            
        except Exception as e:
            self.logger.error(f"Error loading ad input data: {e}")
            return []
    
    def segment_user(self, vehicle_data: Dict) -> str:
        """Determine user segment based on behavior profile"""
        behavior_profile = vehicle_data.get('behavior_profile', {})
        context = vehicle_data.get('context', {})
        vehicle_profile = vehicle_data.get('vehicle_profile', {})
        
        # Scoring for each segment
        segment_scores = {}
        
        # Eco Driver
        eco_score = (
            behavior_profile.get('eco_driving_score', 0.5) * 0.6 +
            (1 - behavior_profile.get('driving_aggressiveness', 0.5)) * 0.4
        )
        segment_scores['eco_driver'] = eco_score
        
        # Performance Enthusiast
        performance_score = (
            behavior_profile.get('driving_aggressiveness', 0.5) * 0.7 +
            (context.get('speed', 50) / 100) * 0.3  # Normalize speed
        )
        segment_scores['performance_enthusiast'] = performance_score
        
        # Safety Conscious
        safety_score = (
            (1 - behavior_profile.get('driving_aggressiveness', 0.5)) * 0.5 +
            (vehicle_profile.get('health_score', 0.8)) * 0.3 +
            (1 if behavior_profile.get('maintenance_needs', False) else 0.7) * 0.2
        )
        segment_scores['safety_conscious'] = safety_score
        
        # Convenience Seeker
        convenience_score = (
            (vehicle_profile.get('health_score', 0.8)) * 0.4 +
            (1 - behavior_profile.get('maintenance_needs', 0)) * 0.6
        )
        segment_scores['convenience_seeker'] = convenience_score
        
        # Return segment with highest score
        best_segment = max(segment_scores.items(), key=lambda x: x[1])
        return best_segment[0]
    
    def calculate_ad_relevance(self, vehicle_data: Dict, recommendations: List[ProductRecommendation]) -> float:
        """Calculate overall ad relevance score"""
        if not recommendations:
            return 0.0
        
        # Average recommendation relevance
        avg_relevance = sum(rec.relevance_score for rec in recommendations) / len(recommendations)
        
        # Boost based on urgency
        behavior_profile = vehicle_data.get('behavior_profile', {})
        if behavior_profile.get('maintenance_needs', False):
            avg_relevance *= 1.2
        
        # Context boost
        context = vehicle_data.get('context', {})
        if context.get('weather') in ['snow', 'rain']:
            avg_relevance *= 1.1
        
        return min(avg_relevance, 1.0)
    
    def generate_ad_headline(self, segment: str, recommendations: List[ProductRecommendation], 
                           vehicle_data: Dict) -> str:
        """Generate compelling ad headline"""
        behavior_profile = vehicle_data.get('behavior_profile', {})
        context = vehicle_data.get('context', {})
        
        # Segment-specific headlines
        if segment == 'eco_driver':
            if any('fuel' in rec.product.tags for rec in recommendations):
                return "🌱 Boost Your Fuel Economy - Save More, Drive Green!"
            return "🌿 Eco-Friendly Automotive Solutions Just for You"
        
        elif segment == 'performance_enthusiast':
            if any('performance' in rec.product.tags for rec in recommendations):
                return "⚡ Unleash Your Vehicle's True Potential!"
            return "🏎️ Performance Upgrades for Serious Drivers"
        
        elif segment == 'safety_conscious':
            if behavior_profile.get('maintenance_needs', False):
                return "🛡️ Keep Your Family Safe - Maintenance Alert!"
            return "🚗 Safety First - Premium Protection for Your Vehicle"
        
        elif segment == 'convenience_seeker':
            return "⚡ Hassle-Free Auto Care - Everything You Need, Delivered"
        
        # Default headline
        return "🔧 Personalized Auto Parts & Accessories"
    
    def generate_ad_message(self, segment: str, recommendations: List[ProductRecommendation],
                          vehicle_data: Dict) -> str:
        """Generate personalized ad message"""
        behavior_profile = vehicle_data.get('behavior_profile', {})
        vehicle_profile = vehicle_data.get('vehicle_profile', {})
        
        message_parts = []
        
        # Opening based on segment
        if segment == 'eco_driver':
            message_parts.append("Maximize your fuel efficiency and reduce environmental impact")
        elif segment == 'performance_enthusiast':
            message_parts.append("Take your driving experience to the next level")
        elif segment == 'safety_conscious':
            message_parts.append("Ensure your vehicle's safety and reliability")
        else:
            message_parts.append("Get the best automotive products for your needs")
        
        # Add urgency if needed
        if behavior_profile.get('maintenance_needs', False):
            message_parts.append("Urgent maintenance recommendations based on your vehicle's condition")
        
        # Add value proposition
        if len(recommendations) > 1:
            total_savings = sum(rec.discount_available or 0 for rec in recommendations if rec.discount_available)
            if total_savings > 0:
                message_parts.append(f"Save up to {total_savings*100:.0f}% with our current offers")
        
        # Add convenience factor
        message_parts.append("Professional installation available. Fast delivery to your location.")
        
        return ". ".join(message_parts) + "."
    
    def generate_call_to_action(self, segment: str, urgency_level: str) -> str:
        """Generate appropriate call-to-action"""
        if urgency_level == 'high':
            return "Schedule Service Now - Book Today!"
        elif segment == 'performance_enthusiast':
            return "Upgrade Now - Unleash Performance!"
        elif segment == 'eco_driver':
            return "Save Money & Planet - Shop Green!"
        elif segment == 'safety_conscious':
            return "Protect Your Family - Order Today!"
        else:
            return "Shop Now - Free Delivery Available!"
    
    def determine_display_format(self, relevance_score: float, urgency_level: str) -> str:
        """Determine optimal display format"""
        if urgency_level == 'high' or relevance_score > 0.8:
            return "popup"  # High attention
        elif relevance_score > 0.6:
            return "banner"  # Medium attention
        else:
            return "native"  # Integrated content
    
    def calculate_budget_allocation(self, relevance_score: float, recommendations: List[ProductRecommendation]) -> float:
        """Calculate advertising budget allocation"""
        base_budget = 25.0  # Base budget per vehicle
        
        # Scale by relevance
        budget = base_budget * relevance_score
        
        # Boost for high-value recommendations
        if recommendations:
            avg_price = sum(rec.product.price for rec in recommendations) / len(recommendations)
            if avg_price > 100:
                budget *= 1.5
        
        return round(budget, 2)
    
    def estimate_ctr(self, segment: str, display_format: str, relevance_score: float) -> float:
        """Estimate click-through rate"""
        base_ctr = {
            'popup': 0.08,
            'banner': 0.05,
            'native': 0.03,
            'video': 0.12
        }
        
        ctr = base_ctr.get(display_format, 0.05)
        
        # Adjust for segment engagement
        segment_multipliers = {
            'performance_enthusiast': 1.3,
            'safety_conscious': 1.1,
            'eco_driver': 1.0,
            'convenience_seeker': 0.9
        }
        
        ctr *= segment_multipliers.get(segment, 1.0)
        
        # Adjust for relevance
        ctr *= (0.5 + relevance_score * 0.5)
        
        return round(ctr, 3)
    
    def create_personalized_ad(self, vehicle_data: Dict, 
                             recommendations: List[ProductRecommendation]) -> PersonalizedAd:
        """Create a personalized advertisement"""
        vehicle_id = vehicle_data.get('vehicle_id', 'unknown')
        
        # User segmentation
        segment = self.segment_user(vehicle_data)
        
        # Calculate relevance
        relevance_score = self.calculate_ad_relevance(vehicle_data, recommendations)
        
        # Determine urgency
        urgency_level = 'high' if vehicle_data.get('behavior_profile', {}).get('maintenance_needs', False) else 'medium'
        
        # Generate ad content
        headline = self.generate_ad_headline(segment, recommendations, vehicle_data)
        message = self.generate_ad_message(segment, recommendations, vehicle_data)
        cta = self.generate_call_to_action(segment, urgency_level)
        
        # Display specifications
        display_format = self.determine_display_format(relevance_score, urgency_level)
        display_duration = 15 if display_format == 'popup' else 30
        
        # Budget and performance
        budget = self.calculate_budget_allocation(relevance_score, recommendations)
        expected_ctr = self.estimate_ctr(segment, display_format, relevance_score)
        
        # Extract user preferences
        user_preferences = {
            'segment': segment,
            'price_sensitivity': 1 - vehicle_data.get('vehicle_profile', {}).get('health_score', 0.8),
            'urgency_level': urgency_level,
            'maintenance_awareness': vehicle_data.get('behavior_profile', {}).get('maintenance_needs', False)
        }
        
        # Contextual triggers
        context = vehicle_data.get('context', {})
        contextual_triggers = [
            f"Weather: {context.get('weather', 'clear')}",
            f"Terrain: {context.get('terrain', 'mixed')}",
            f"Speed: {context.get('speed', 50)} km/h"
        ]
        
        ad_id = f"AD_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        ad = PersonalizedAd(
            ad_id=ad_id,
            vehicle_id=vehicle_id,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            headline=headline,
            message=message,
            call_to_action=cta,
            featured_products=recommendations[:3],  # Top 3 recommendations
            target_segment=segment,
            relevance_score=relevance_score,
            display_format=display_format,
            display_duration=display_duration,
            display_locations=['infotainment', 'mobile'],
            campaign_type='behavioral_targeting',
            budget_allocation=budget,
            expected_ctr=expected_ctr,
            user_preferences=user_preferences,
            contextual_triggers=contextual_triggers
        )
        
        return ad
    
    def process_ad_engine_data(self) -> List[PersonalizedAd]:
        """Main processing function - generate ads for all vehicles"""
        self.logger.info("Processing Ad Engine data...")
        
        # Load Branch 3 data
        ad_input_data = self.load_ad_input_data()
        
        if not ad_input_data:
            self.logger.warning("No ad input data found")
            return []
        
        generated_ads = []
        all_recommendations = []
        
        # Process each vehicle
        for vehicle_data in ad_input_data:
            try:
                vehicle_id = vehicle_data.get('vehicle_id', 'unknown')
                
                # Generate product recommendations
                recommendations = self.recommendation_engine.generate_recommendations(vehicle_data)
                all_recommendations.extend(recommendations)
                
                if recommendations:
                    # Create personalized ad
                    ad = self.create_personalized_ad(vehicle_data, recommendations)
                    generated_ads.append(ad)
                    
                    self.logger.info(f"Generated ad for {vehicle_id}: {ad.target_segment} segment, "
                                   f"{len(recommendations)} products, ${ad.budget_allocation} budget")
                else:
                    self.logger.warning(f"No recommendations generated for {vehicle_id}")
                
                self.ad_stats['vehicles_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {vehicle_data.get('vehicle_id', 'unknown')}: {e}")
        
        # Update statistics
        self.ad_stats['recommendations_generated'] = len(all_recommendations)
        self.ad_stats['ads_created'] = len(generated_ads)
        self.ad_stats['total_budget_allocated'] = sum(ad.budget_allocation for ad in generated_ads)
        
        # Save outputs
        self.save_recommendations(all_recommendations)
        self.save_advertisements(generated_ads)
        self.generate_campaign_summary(generated_ads)
        
        self.logger.info(f"Ad processing complete: {len(generated_ads)} ads generated")
        return generated_ads
    
    def save_recommendations(self, recommendations: List[ProductRecommendation]):
        """Save product recommendations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"recommendations/product_recommendations_{timestamp}.jsonl"
        
        with open(output_file, 'w') as f:
            for rec in recommendations:
                f.write(json.dumps(asdict(rec)) + '\n')
        
        self.logger.info(f"Saved {len(recommendations)} recommendations to {output_file}")
    
    def save_advertisements(self, ads: List[PersonalizedAd]):
        """Save personalized advertisements"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"ads/personalized_ads_{timestamp}.jsonl"
        
        with open(output_file, 'w') as f:
            for ad in ads:
                f.write(json.dumps(asdict(ad)) + '\n')
        
        self.logger.info(f"Saved {len(ads)} personalized ads to {output_file}")
    
    def generate_campaign_summary(self, ads: List[PersonalizedAd]):
        """Generate advertising campaign summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Calculate analytics
        segment_distribution = {}
        format_distribution = {}
        total_budget = 0.0
        avg_relevance = 0.0
        
        for ad in ads:
            # Segment distribution
            segment_distribution[ad.target_segment] = segment_distribution.get(ad.target_segment, 0) + 1
            
            # Format distribution
            format_distribution[ad.display_format] = format_distribution.get(ad.display_format, 0) + 1
            
            # Budget and relevance
            total_budget += ad.budget_allocation
            avg_relevance += ad.relevance_score
        
        if ads:
            avg_relevance /= len(ads)
        
        # Product category analysis
        all_products = []
        for ad in ads:
            all_products.extend([rec.product for rec in ad.featured_products])
        
        category_counts = {}
        for product in all_products:
            category_counts[product.category] = category_counts.get(product.category, 0) + 1
        
        summary = {
            'campaign_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'campaign_overview': {
                'total_ads_created': len(ads),
                'total_budget_allocated': round(total_budget, 2),
                'average_relevance_score': round(avg_relevance, 3),
                'expected_total_clicks': sum(ad.expected_ctr * 1000 for ad in ads)  # Assuming 1000 impressions each
            },
            'targeting_analysis': {
                'segment_distribution': segment_distribution,
                'display_format_distribution': format_distribution
            },
            'product_analysis': {
                'total_products_featured': len(all_products),
                'category_distribution': category_counts,
                'average_product_price': round(sum(p.price for p in all_products) / len(all_products) if all_products else 0, 2)
            },
            'performance_predictions': {
                'estimated_ctr_range': f"{min(ad.expected_ctr for ad in ads):.3f} - {max(ad.expected_ctr for ad in ads):.3f}",
                'top_performing_segment': max(segment_distribution.items(), key=lambda x: x[1])[0] if segment_distribution else None
            },
            'processing_statistics': self.ad_stats
        }
        
        output_file = f"campaigns/campaign_summary_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Generated campaign summary: {output_file}")

if __name__ == "__main__":
    # Run Ad Engine Service
    ad_engine = AdEngineService()
    
    try:
        print("Starting Ad & Recommendation Engine Service...")
        print("Processing data from Branch 3 (Ad Engine) of Data Processing Service...")
        print()
        
        # Process all ad data
        ads = ad_engine.process_ad_engine_data()
        
        if ads:
            print("\n=== AD ENGINE RESULTS ===")
            print(f"Total ads generated: {len(ads)}")
            
            # Segment analysis
            segments = {}
            for ad in ads:
                segments[ad.target_segment] = segments.get(ad.target_segment, 0) + 1
            
            print("User Segment Distribution:")
            for segment, count in segments.items():
                print(f"  {segment.replace('_', ' ').title()}: {count} ads")
            
            # Budget analysis
            total_budget = sum(ad.budget_allocation for ad in ads)
            print(f"\nCampaign Budget: ${total_budget:.2f}")
            print(f"Average budget per ad: ${total_budget/len(ads):.2f}")
            
            # Top ads
            top_ads = sorted(ads, key=lambda x: x.relevance_score, reverse=True)[:3]
            print(f"\nTop Performing Ads (by relevance):")
            for i, ad in enumerate(top_ads, 1):
                print(f"  {i}. {ad.vehicle_id}: {ad.headline}")
                print(f"     Relevance: {ad.relevance_score:.3f} | Budget: ${ad.budget_allocation}")
            
            print(f"\nGenerated files:")
            print(f"  - recommendations/: Product recommendations")
            print(f"  - ads/: Personalized advertisements")
            print(f"  - campaigns/: Campaign analytics")
        else:
            print("No ads generated - check input data from Branch 3")
            
    except Exception as e:
        print(f"Ad Engine processing failed: {e}")
        import traceback
        traceback.print_exc()
