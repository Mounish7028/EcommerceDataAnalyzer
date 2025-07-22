import logging
from typing import List, Dict, Any, Optional
from database import DatabaseManager
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get comprehensive business performance summary"""
        try:
            # Total sales and revenue metrics
            sales_query = """
            SELECT 
                SUM(total_sales) as total_revenue,
                SUM(total_units_ordered) as total_units,
                COUNT(DISTINCT item_id) as active_products,
                AVG(total_sales) as avg_sales_per_transaction,
                COUNT(DISTINCT date) as active_days
            FROM total_sales WHERE total_sales > 0
            """
            
            # Ad performance metrics
            ad_query = """
            SELECT 
                SUM(ad_sales) as total_ad_revenue,
                SUM(ad_spend) as total_ad_spend,
                SUM(impressions) as total_impressions,
                SUM(clicks) as total_clicks,
                SUM(units_sold) as total_ad_units,
                CASE WHEN SUM(ad_spend) > 0 THEN SUM(ad_sales) / SUM(ad_spend) ELSE 0 END as overall_roas,
                CASE WHEN SUM(clicks) > 0 THEN SUM(ad_spend) / SUM(clicks) ELSE 0 END as avg_cpc,
                CASE WHEN SUM(impressions) > 0 THEN SUM(clicks) * 100.0 / SUM(impressions) ELSE 0 END as overall_ctr,
                CASE WHEN SUM(clicks) > 0 THEN SUM(units_sold) * 100.0 / SUM(clicks) ELSE 0 END as overall_conversion_rate
            FROM ad_sales WHERE ad_spend > 0
            """
            
            # Eligibility metrics
            eligibility_query = """
            SELECT 
                SUM(CASE WHEN eligibility = 'TRUE' THEN 1 ELSE 0 END) as eligible_products,
                COUNT(*) as total_products_checked,
                SUM(CASE WHEN eligibility = 'TRUE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as eligibility_rate
            FROM (
                SELECT DISTINCT item_id, eligibility 
                FROM eligibility 
                WHERE eligibility_datetime_utc = (
                    SELECT MAX(eligibility_datetime_utc) 
                    FROM eligibility e2 
                    WHERE e2.item_id = eligibility.item_id
                )
            ) latest_eligibility
            """
            
            sales_results = self.db_manager.execute_query(sales_query)
            ad_results = self.db_manager.execute_query(ad_query)
            eligibility_results = self.db_manager.execute_query(eligibility_query)
            
            summary = {
                'sales_metrics': sales_results[0] if sales_results else {},
                'ad_metrics': ad_results[0] if ad_results else {},
                'eligibility_metrics': eligibility_results[0] if eligibility_results else {},
                'generated_at': datetime.now().isoformat()
            }
            
            # Calculate additional derived metrics
            if sales_results and ad_results:
                sales_data = sales_results[0]
                ad_data = ad_results[0]
                
                # Ad efficiency metrics
                if sales_data.get('total_revenue', 0) > 0:
                    summary['derived_metrics'] = {
                        'ad_revenue_percentage': (ad_data.get('total_ad_revenue', 0) / sales_data.get('total_revenue', 1)) * 100,
                        'revenue_per_product': sales_data.get('total_revenue', 0) / max(sales_data.get('active_products', 1), 1),
                        'ad_spend_efficiency': ad_data.get('total_ad_revenue', 0) - ad_data.get('total_ad_spend', 0)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating business summary: {str(e)}")
            return {}
    
    def get_product_performance_analysis(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get detailed performance analysis for top products"""
        try:
            query = f"""
            SELECT 
                ts.item_id,
                SUM(ts.total_sales) as total_revenue,
                SUM(ts.total_units_ordered) as total_units,
                SUM(ads.ad_sales) as ad_revenue,
                SUM(ads.ad_spend) as ad_spend,
                SUM(ads.impressions) as impressions,
                SUM(ads.clicks) as clicks,
                SUM(ads.units_sold) as ad_units,
                CASE WHEN SUM(ads.ad_spend) > 0 THEN SUM(ads.ad_sales) / SUM(ads.ad_spend) ELSE 0 END as roas,
                CASE WHEN SUM(ads.clicks) > 0 THEN SUM(ads.ad_spend) / SUM(ads.clicks) ELSE 0 END as cpc,
                CASE WHEN SUM(ads.impressions) > 0 THEN SUM(ads.clicks) * 100.0 / SUM(ads.impressions) ELSE 0 END as ctr,
                CASE WHEN SUM(ads.clicks) > 0 THEN SUM(ads.units_sold) * 100.0 / SUM(ads.clicks) ELSE 0 END as conversion_rate,
                e.eligibility as is_eligible
            FROM total_sales ts
            LEFT JOIN ad_sales ads ON ts.item_id = ads.item_id
            LEFT JOIN (
                SELECT DISTINCT item_id, eligibility 
                FROM eligibility 
                WHERE eligibility_datetime_utc = (
                    SELECT MAX(eligibility_datetime_utc) 
                    FROM eligibility e2 
                    WHERE e2.item_id = eligibility.item_id
                )
            ) e ON ts.item_id = e.item_id
            WHERE ts.total_sales > 0
            GROUP BY ts.item_id, e.eligibility
            ORDER BY total_revenue DESC
            LIMIT {limit}
            """
            
            results = self.db_manager.execute_query(query)
            
            # Add performance ratings
            for product in results:
                product['performance_score'] = self._calculate_performance_score(product)
                product['recommendations'] = self._generate_product_recommendations(product)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting product performance analysis: {str(e)}")
            return []
    
    def _calculate_performance_score(self, product: Dict[str, Any]) -> float:
        """Calculate a performance score (0-100) for a product"""
        score = 0
        
        # Revenue component (40%)
        revenue = product.get('total_revenue', 0)
        if revenue > 10000:
            score += 40
        elif revenue > 5000:
            score += 30
        elif revenue > 1000:
            score += 20
        elif revenue > 0:
            score += 10
        
        # RoAS component (30%)
        roas = product.get('roas', 0)
        if roas > 10:
            score += 30
        elif roas > 5:
            score += 25
        elif roas > 3:
            score += 20
        elif roas > 2:
            score += 15
        elif roas > 1:
            score += 10
        
        # Conversion rate component (20%)
        conversion_rate = product.get('conversion_rate', 0)
        if conversion_rate > 10:
            score += 20
        elif conversion_rate > 5:
            score += 15
        elif conversion_rate > 2:
            score += 10
        elif conversion_rate > 1:
            score += 5
        
        # Eligibility component (10%)
        if product.get('is_eligible') == 'TRUE':
            score += 10
        
        return min(score, 100)
    
    def _generate_product_recommendations(self, product: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for a product"""
        recommendations = []
        
        roas = product.get('roas', 0)
        cpc = product.get('cpc', 0)
        conversion_rate = product.get('conversion_rate', 0)
        ctr = product.get('ctr', 0)
        is_eligible = product.get('is_eligible')
        
        # RoAS recommendations
        if roas < 2:
            recommendations.append("⚠️ Low RoAS: Consider optimizing ad targeting or reducing ad spend")
        elif roas > 10:
            recommendations.append("🚀 Excellent RoAS: Consider increasing ad budget to scale")
        
        # CPC recommendations
        if cpc > 5:
            recommendations.append("💰 High CPC: Review keyword bidding strategy and ad relevance")
        elif cpc < 0.5:
            recommendations.append("💡 Low CPC: Opportunity to increase bids for better visibility")
        
        # Conversion rate recommendations
        if conversion_rate < 1:
            recommendations.append("📈 Low conversion rate: Optimize product page and ad copy")
        elif conversion_rate > 10:
            recommendations.append("✅ Excellent conversion rate: This product converts very well")
        
        # CTR recommendations
        if ctr < 1:
            recommendations.append("👁️ Low CTR: Improve ad creative and targeting")
        elif ctr > 5:
            recommendations.append("🎯 Great CTR: Ad creative is engaging audiences well")
        
        # Eligibility recommendations
        if is_eligible != 'TRUE':
            recommendations.append("❌ Not eligible for ads: Review eligibility requirements")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def get_time_based_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get time-based performance analysis"""
        try:
            # Daily sales trend
            daily_sales_query = f"""
            SELECT 
                date,
                SUM(total_sales) as daily_sales,
                SUM(total_units_ordered) as daily_units,
                COUNT(DISTINCT item_id) as active_products
            FROM total_sales 
            WHERE total_sales > 0 
            GROUP BY date 
            ORDER BY date DESC 
            LIMIT {days}
            """
            
            # Daily ad performance
            daily_ad_query = f"""
            SELECT 
                date,
                SUM(ad_sales) as daily_ad_sales,
                SUM(ad_spend) as daily_ad_spend,
                SUM(impressions) as daily_impressions,
                SUM(clicks) as daily_clicks,
                CASE WHEN SUM(ad_spend) > 0 THEN SUM(ad_sales) / SUM(ad_spend) ELSE 0 END as daily_roas
            FROM ad_sales 
            WHERE ad_spend > 0 
            GROUP BY date 
            ORDER BY date DESC 
            LIMIT {days}
            """
            
            sales_data = self.db_manager.execute_query(daily_sales_query)
            ad_data = self.db_manager.execute_query(daily_ad_query)
            
            # Calculate trends
            analysis = {
                'daily_sales': sales_data,
                'daily_ad_performance': ad_data,
                'trends': self._calculate_trends(sales_data, ad_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting time-based analysis: {str(e)}")
            return {}
    
    def _calculate_trends(self, sales_data: List[Dict], ad_data: List[Dict]) -> Dict[str, str]:
        """Calculate trend indicators"""
        trends = {}
        
        if len(sales_data) >= 2:
            recent_sales = sales_data[0].get('daily_sales', 0)
            previous_sales = sales_data[1].get('daily_sales', 0)
            
            if previous_sales > 0:
                sales_change = ((recent_sales - previous_sales) / previous_sales) * 100
                if sales_change > 10:
                    trends['sales_trend'] = f"📈 Sales up {sales_change:.1f}%"
                elif sales_change < -10:
                    trends['sales_trend'] = f"📉 Sales down {abs(sales_change):.1f}%"
                else:
                    trends['sales_trend'] = "➡️ Sales stable"
        
        if len(ad_data) >= 2:
            recent_roas = ad_data[0].get('daily_roas', 0)
            previous_roas = ad_data[1].get('daily_roas', 0)
            
            if previous_roas > 0:
                roas_change = ((recent_roas - previous_roas) / previous_roas) * 100
                if roas_change > 10:
                    trends['roas_trend'] = f"📈 RoAS improving {roas_change:.1f}%"
                elif roas_change < -10:
                    trends['roas_trend'] = f"📉 RoAS declining {abs(roas_change):.1f}%"
                else:
                    trends['roas_trend'] = "➡️ RoAS stable"
        
        return trends