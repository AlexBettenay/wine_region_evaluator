import pandas as pd
from main.models import Region
from datetime import date
from typing import List

def analyze_seasonal_suitability(region: Region) -> List[str]:
    """
    Determine the best time of year for grape growing in a Region.
    
    Parameters:
        region (Region): A model instance representing a wine growing region with
            associated climate_readings.
    
    Returns:
        A list of strings: The best consecutive 3-month period for grape growing in the region.
    """
    # Get all readings for this region
    readings = region.climate_readings.all()
    
    # Add evaluation score to each reading
    evaluated_readings = []
    for reading in readings:
        score = reading.evaluate()
        evaluated_readings.append({
            'date': reading.date,
            'month': reading.date.month,
            'score': score
        })
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(evaluated_readings)
    
    # Calculate average score by month
    monthly_avg = df.groupby('month')['score'].mean().sort_values(ascending=False)
    
    # Identify best consecutive 3-month period (growing season)
    # This is a simplified approach - you could make it more sophisticated
    best_month = monthly_avg.idxmax()
    growing_season = [(best_month + i) % 12 or 12 for i in range(3)]
    
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                   5: 'May', 6: 'June', 7: 'July', 8: 'August', 
                   9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    return [month_names[m] for m in growing_season]

def analyze_longterm_viability(region: Region, time_period: int = 30) -> float:
    """
    Calculate percentage of time with optimal conditions over last 30 years.
    
    Parameters:
        region (Region): A model instance representing a wine growing region.
        time_period (int): Number of years to consider for long-term viability analysis (optional, defaults to 30 years).
    
    Returns:
        A float: Percentage of time with optimal conditions for grape growing over the time period,
    """

    time_period_date = date(date.today().year - time_period, date.today().month, date.today().day)
    
    # Get readings for this region from the last 30 years
    readings = region.climate_readings.filter(date__gte=time_period_date)
    
    total_days = readings.count()
    if total_days == 0:
        return 0
    
    # Count days with good conditions (score >= 70)
    optimal_days = 0
    for reading in readings:
        score = reading.evaluate()
        if score >= 70:
            optimal_days += 1
    
    # Calculate percentage
    percentage = (optimal_days / total_days) * 100
    
    return round(percentage, 2)

def analyze_historical_performance(region: List[Region], time_period: int=10) -> float:
    """
    Find the region with worst climate for grape growing over past 10 years

    Parameters:
        region (Region): A model instance representing a wine growing region.
        time_period (int): Number of years to consider for historical performance analysis (optional, defaults to 10 years)

    Returns:
        A float: Average score for the region over the time period.
    """
    
    time_period_date = date(date.today().year - time_period, date.today().month, date.today().day)

    readings = region.climate_readings.filter(
            date__gte=time_period_date
        )
    
    total_score = 0
    for reading in readings:
            total_score += reading.evaluate()

    return round((total_score / readings.count() if readings.count() > 0 else 0), 2)
