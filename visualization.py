import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)

class VisualizationEngine:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_sales_trend_chart(self) -> Optional[str]:
        """Create a sales trend chart over time"""
        try:
            query = """
            SELECT date, SUM(total_sales) as daily_sales, SUM(total_units_ordered) as daily_units
            FROM total_sales 
            WHERE total_sales > 0
            GROUP BY date 
            ORDER BY date
            """
            results = self.db_manager.execute_query(query)
            
            if not results:
                return None
                
            df = pd.DataFrame(results)
            df['date'] = pd.to_datetime(df['date'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['daily_sales'],
                mode='lines+markers',
                name='Daily Sales ($)',
                line=dict(color='#28a745', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Daily Sales Trend',
                xaxis_title='Date',
                yaxis_title='Sales ($)',
                template='plotly_dark',
                height=400,
                showlegend=True
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating sales trend chart: {str(e)}")
            return None
    
    def create_top_products_chart(self, limit: int = 10) -> Optional[str]:
        """Create a chart showing top products by sales"""
        try:
            query = f"""
            SELECT item_id, SUM(total_sales) as total_product_sales, SUM(total_units_ordered) as total_units
            FROM total_sales 
            WHERE total_sales > 0
            GROUP BY item_id 
            ORDER BY total_product_sales DESC 
            LIMIT {limit}
            """
            results = self.db_manager.execute_query(query)
            
            if not results:
                return None
                
            df = pd.DataFrame(results)
            df['item_id'] = df['item_id'].astype(str)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['item_id'],
                    y=df['total_product_sales'],
                    marker_color='#007bff',
                    text=df['total_product_sales'].round(2),
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title=f'Top {limit} Products by Sales',
                xaxis_title='Product ID',
                yaxis_title='Total Sales ($)',
                template='plotly_dark',
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating top products chart: {str(e)}")
            return None
    
    def create_roas_by_product_chart(self, limit: int = 15) -> Optional[str]:
        """Create a chart showing RoAS by product"""
        try:
            query = f"""
            SELECT 
                item_id,
                SUM(ad_sales) as total_ad_sales,
                SUM(ad_spend) as total_ad_spend,
                CASE 
                    WHEN SUM(ad_spend) > 0 THEN SUM(ad_sales) / SUM(ad_spend)
                    ELSE 0 
                END as roas
            FROM ad_sales 
            WHERE ad_spend > 0 AND ad_sales > 0
            GROUP BY item_id 
            ORDER BY roas DESC 
            LIMIT {limit}
            """
            results = self.db_manager.execute_query(query)
            
            if not results:
                return None
                
            df = pd.DataFrame(results)
            df['item_id'] = df['item_id'].astype(str)
            
            # Color code based on RoAS performance
            colors = ['#28a745' if x >= 5 else '#ffc107' if x >= 2 else '#dc3545' for x in df['roas']]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['item_id'],
                    y=df['roas'],
                    marker_color=colors,
                    text=df['roas'].round(2),
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title=f'Return on Ad Spend (RoAS) by Product - Top {limit}',
                xaxis_title='Product ID',
                yaxis_title='RoAS (Revenue/Ad Spend)',
                template='plotly_dark',
                height=400,
                annotations=[
                    dict(
                        text="Green: Excellent (≥5x) | Yellow: Good (≥2x) | Red: Poor (<2x)",
                        xref="paper", yref="paper",
                        x=0.5, y=1.1, xanchor='center', yanchor='bottom',
                        showarrow=False,
                        font=dict(size=12)
                    )
                ]
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating RoAS chart: {str(e)}")
            return None
    
    def create_eligibility_pie_chart(self) -> Optional[str]:
        """Create a pie chart showing product eligibility distribution"""
        try:
            query = """
            SELECT 
                eligibility,
                COUNT(*) as count
            FROM (
                SELECT DISTINCT item_id, eligibility 
                FROM eligibility 
                WHERE eligibility_datetime_utc = (
                    SELECT MAX(eligibility_datetime_utc) 
                    FROM eligibility e2 
                    WHERE e2.item_id = eligibility.item_id
                )
            ) latest_eligibility
            GROUP BY eligibility
            """
            results = self.db_manager.execute_query(query)
            
            if not results:
                return None
                
            df = pd.DataFrame(results)
            
            colors = ['#28a745' if status == 'TRUE' else '#dc3545' for status in df['eligibility']]
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=[f"{'Eligible' if x == 'TRUE' else 'Not Eligible'}" for x in df['eligibility']],
                    values=df['count'],
                    marker_colors=colors,
                    textinfo='label+percent+value',
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='Product Eligibility Distribution',
                template='plotly_dark',
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating eligibility pie chart: {str(e)}")
            return None
    
    def create_ad_performance_scatter(self) -> Optional[str]:
        """Create a scatter plot of ad performance (CPC vs Conversion Rate)"""
        try:
            query = """
            SELECT 
                item_id,
                SUM(ad_spend) as total_spend,
                SUM(clicks) as total_clicks,
                SUM(units_sold) as total_conversions,
                CASE 
                    WHEN SUM(clicks) > 0 THEN SUM(ad_spend) * 1.0 / SUM(clicks)
                    ELSE 0 
                END as cpc,
                CASE 
                    WHEN SUM(clicks) > 0 THEN SUM(units_sold) * 100.0 / SUM(clicks)
                    ELSE 0 
                END as conversion_rate
            FROM ad_sales 
            WHERE clicks > 0 AND ad_spend > 0
            GROUP BY item_id
            HAVING SUM(ad_spend) > 10
            """
            results = self.db_manager.execute_query(query)
            
            if not results:
                return None
                
            df = pd.DataFrame(results)
            
            fig = go.Figure(data=go.Scatter(
                x=df['cpc'],
                y=df['conversion_rate'],
                mode='markers',
                marker=dict(
                    size=df['total_spend'].apply(lambda x: min(max(x/10, 5), 30)),
                    color=df['conversion_rate'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Conversion Rate %")
                ),
                text=df['item_id'].astype(str),
                textposition="middle center",
                hovertemplate='<b>Product %{text}</b><br>' +
                             'CPC: $%{x:.2f}<br>' +
                             'Conversion Rate: %{y:.1f}%<br>' +
                             'Total Spend: $%{marker.size:.0f}<br>' +
                             '<extra></extra>'
            ))
            
            fig.update_layout(
                title='Ad Performance: Cost Per Click vs Conversion Rate',
                xaxis_title='Cost Per Click ($)',
                yaxis_title='Conversion Rate (%)',
                template='plotly_dark',
                height=500,
                annotations=[
                    dict(
                        text="Bubble size = Ad Spend | Color = Conversion Rate",
                        xref="paper", yref="paper",
                        x=0.5, y=1.1, xanchor='center', yanchor='bottom',
                        showarrow=False,
                        font=dict(size=12)
                    )
                ]
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating ad performance scatter: {str(e)}")
            return None
    
    def get_visualization_for_question(self, question: str, results: List[Dict[str, Any]]) -> Optional[str]:
        """Determine and create appropriate visualization based on the question"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ['sales trend', 'daily sales', 'sales over time']):
            return self.create_sales_trend_chart()
        elif any(keyword in question_lower for keyword in ['top products', 'best selling', 'highest sales']):
            return self.create_top_products_chart()
        elif any(keyword in question_lower for keyword in ['roas', 'return on ad spend', 'ad performance']):
            return self.create_roas_by_product_chart()
        elif any(keyword in question_lower for keyword in ['eligibility', 'eligible products']):
            return self.create_eligibility_pie_chart()
        elif any(keyword in question_lower for keyword in ['cpc', 'cost per click', 'conversion']):
            return self.create_ad_performance_scatter()
        
        # Default visualization based on data type
        if results and len(results) > 1:
            # If multiple rows, try to create a relevant chart
            first_row = results[0]
            if 'item_id' in first_row and any('sales' in k.lower() for k in first_row.keys()):
                return self.create_top_products_chart()
            elif 'date' in first_row:
                return self.create_sales_trend_chart()
        
        return None