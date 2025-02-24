import pandas as pd
import numpy as np
import datetime
import random
import matplotlib.pyplot as plt
import math
import calendar



def get_season(month):
    """Determines the season based on the month (for the Southern Hemisphere)."""
    if month in [12, 1, 2]:
        return "Summer"
    elif month in [3, 4, 5]:
        return "Autumn"
    elif month in [6, 7, 8]:
        return "Winter"
    else:
        return "Spring"

def exponential_smoothing(previous_value, current_value, alpha=0.05):
    """Simple exponential smoothing for gradual transitions."""
    return alpha * current_value + (1 - alpha) * previous_value

def calculate_seasonal_temp_adjustment(month, year_variation_temp):
    """Calculates the seasonal temperature adjustment with annual variation."""
    base_adjustment = 0
    if month in [12, 1, 2]: 
        base_adjustment = 0.5
    elif month in [6, 7, 8]: 
        base_adjustment = -1.5
    return base_adjustment + year_variation_temp

def calculate_seasonal_humidity_adjustment(month, year_variation_humidity):
    """Calculates the seasonal humidity adjustment with annual variation."""
    base_adjustment = 0
    if month in [12, 1, 2]: 
        base_adjustment = 5
    elif month in [6, 7, 8]: 
        base_adjustment = 8
    elif month in [3, 4, 5]: 
        base_adjustment = -3
    return base_adjustment + year_variation_humidity

def internal_temp_by_hour(current_date, hour, base_temp_active_hours, base_temp_inactive_hours, smoothed_seasonal_temp_adjustment=0, noise_level_temp=0.2):
    """Simulates the internal temperature of the hive with annual variation based and noise."""
    seasonal_adjustment = smoothed_seasonal_temp_adjustment

    if 8 <= hour <= 18: 
        base_temp = base_temp_active_hours + seasonal_adjustment + 1.0
    else:              
        base_temp = base_temp_inactive_hours + seasonal_adjustment

    temp = base_temp + random.uniform(-noise_level_temp, noise_level_temp) 
    return round(np.clip(temp, 30.0, 37.0), 1) 

def internal_humidity_by_hour(current_date, hour, base_humidity_active_hours, base_humidity_inactive_hours, smoothed_seasonal_humidity_adjustment=0, noise_level_humidity=2):
    """Simulates the internal humidity of the hive with annual variation based and noise."""
    seasonal_adjustment = smoothed_seasonal_humidity_adjustment

    if 8 <= hour <= 18: 
        base_humidity = base_humidity_active_hours + seasonal_adjustment
    else:              
        base_humidity = base_humidity_inactive_hours + seasonal_adjustment

    humidity = base_humidity + random.uniform(-noise_level_humidity, noise_level_humidity) 
    return round(np.clip(humidity, 60, 80), 1) 

def weight_by_season_and_harvest(month, day_of_month, prev_weight=None, beehive_factor=1,
                                 harvest_date=None, current_date=None, post_harvest=False, harvest_percentage=0.4, min_weight_limit=20):
    """
    Simulates hive weight with a realistic annual cycle, percentage harvest, and gradual decline.
    Uses weekly changes and daily noise for a smooth curve.
    """
    if prev_weight is None:
        prev_weight = random.uniform(20, 30) 

    weekly_weight_change = {  
        1:  [0.5, 0.55, 0.6, 0.65],    
        2:  [-0.15, -0.1, -0.05, 0.0],  
        3:  [-0.3, -0.25, -0.2, -0.15],   
        4:  [-0.25, -0.2, -0.15, -0.1],   
        5:  [-0.15, -0.1, -0.05, 0.0],    
        6:  [0.0, 0.05, 0.1, 0.15],     
        7:  [0.4, 0.45, 0.5, 0.55],     
        8:  [0.5, 0.55, 0.6, 0.65],     
        9:  [0.7, 0.75, 0.8, 0.85],     
        10: [0.9, 0.95, 1.0, 1.05],     
        11: [1.05, 1.0, 0.95, 0.9],     
        12: [0.6, 0.55, 0.5, 0.45]      
    }
    week_of_month = min((day_of_month - 1) // 7, 3) 
    daily_increment = (weekly_weight_change.get(month, [0,0,0,0])[week_of_month] * beehive_factor) / 7 
    daily_increment += random.uniform(-0.02, 0.02) 

    new_weight = prev_weight + daily_increment 


    
    print(f"\n--- weight_by_season_and_harvest ---")
    print(f"  Date: {current_date}, Month: {month}, Day of Month: {day_of_month}")
    print(f"  Previous Weight (input): {prev_weight:.2f}, Post_harvest Flag: {post_harvest}") 


    if current_date.month == 2 and current_date.day == harvest_date.day and not post_harvest: 
        harvest_amount = prev_weight * harvest_percentage 
        new_weight = prev_weight - harvest_amount 
        post_harvest = True 
        print(f"  ¡HARVEST IN FEBRUARY! Hive (factor {beehive_factor}): Weight before: {prev_weight:.2f}, "
              f"  Harvested: {harvest_amount:.2f} ({harvest_percentage*100:.0f}%), Weight after: {new_weight:.2f}")
    elif current_date.month != 2: 
        post_harvest = False

    
    if current_date.year == start_date.year and month in [1, 2]: 
        min_base_weight = 20 
        max_weight = 60 
        new_weight = max(min_base_weight, new_weight) 
        new_weight = min(max_weight, new_weight) 

        print(f"  --- Jan/Feb Weight Change ---")
        print(f"    daily_increment: {daily_increment:.4f}")
        print(f"    new_weight (before clip): {prev_weight + daily_increment:.2f}")
        print(f"    min_base_weight: {min_base_weight}, max_weight: {max_weight}")
        print(f"    new_weight (after clip): {new_weight:.2f}")


    print(f"  New Weight (output): {new_weight:.2f}, Post_harvest Flag (after): {post_harvest}") 
    return round(new_weight, 2), post_harvest 

def sound_by_activity():
    """Simulates sound level based on activity."""
    base_sound = 40
    return int(base_sound + random.uniform(-5, 5)) 

def co2_by_activity():
    """Simulates CO2 level based on activity."""
    base_co2 = 400
    return int(base_co2 + random.uniform(-50, 50)) 

def voc_by_activity():
    """Simulates VOCs level based on activity."""
    return "Medium" 

def sun_exposure(hour):
    """Determines sun exposure based on hour."""
    sunrise = random.randint(6, 8)
    sunset = random.randint(18, 20)
    if sunrise <= hour <= sunset: 
        return "Sun"
    else:                      
        return "Shade"

def calculate_seasonal_factor(month):
    """Calculates seasonal factor for activity, peak in summer and spring."""
    targets = { 
        1: 1.0, 2: 1.0, 3: 0.3, 4: 0.3, 5: 0.3, 6: 0.3,
        7: 0.3, 8: 0.3, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0
    }
    return targets.get(month, 0.3) 


start_date = datetime.date(2019, 1, 1)
end_date = datetime.date(2025, 12, 31)
num_days = (end_date - start_date).days + 1

num_beehives = 30 
data = [] 
prev_values = {} 
dim_beehive_data = [] 

base_latitude = -35.0421812  
base_longitude = -58.5391796 

for beehive_id in range(1, num_beehives + 1): 
    beehive_factor = random.uniform(0.8, 1.2) 
    harvest_day = random.randint(1, 28) 

    
    prev_values[beehive_id] = {
        "weight": None, 
        "temp": None,
        "humidity": None,
        "harvest_index": 0,
        "post_harvest": False, 
        "seasonal_factor": 0.5,
        "seasonal_temp_adjustment": 0,
        "seasonal_humidity_adjustment": 0,
        "harvest_day": harvest_day,
        "min_weight": float('inf') 
    }
    
    initial_weight = random.uniform(20, 30) 
    prev_values[beehive_id]["weight"] = initial_weight 
    print(f"Beehive {beehive_id}: Initial Weight = {initial_weight:.2f} kg") 

    
    latitude = base_latitude + random.uniform(-0.01, 0.01) 
    longitude = base_longitude + random.uniform(-0.01, 0.01) 
    beehive_location = f"{latitude:.6f},{longitude:.6f}"

    for year_offset in range(end_date.year - start_date.year + 1): 
        current_start_year = start_date.year + year_offset
        current_end_year = current_start_year
        if year_offset < (end_date.year - start_date.year):
            current_end_date_year = datetime.date(current_end_year, 12, 31)
        else:
            current_end_date_year = end_date

        current_start_date_year = datetime.date(current_start_year, 1, 1)
        num_days_year = (current_end_date_year - current_start_date_year).days + 1
        harvest_date = datetime.date(current_start_year + 1, 2, prev_values[beehive_id]["harvest_day"]) 
        harvest_dates_year = [harvest_date]

        
        year_variation_temp = random.uniform(-0.5, 0.5) 
        year_variation_humidity = random.uniform(-2, 2) 
        base_temp_active_hours_year = 33.5 + random.uniform(-0.3, 0.3) 
        base_temp_inactive_hours_year = 32.5 + random.uniform(-0.3, 0.3) 
        base_humidity_active_hours_year = 65 + random.uniform(-1.5, 1.5) 
        base_humidity_inactive_hours_year = 70 + random.uniform(-1.5, 1.5) 
        noise_level_temp_year = 0.2 + random.uniform(-0.05, 0.05) 
        noise_level_humidity_year = 2 + random.uniform(-0.5, 0.5) 

        
        prev_values[beehive_id]["harvest_index"] = 0 
        prev_values[beehive_id]["post_harvest"] = False 

        for day in range(num_days_year): 
            current_date = current_start_date_year + datetime.timedelta(days=day)
            day_of_month = current_date.day 
            season = get_season(current_date.month) 

            
            target_seasonal_temp_adjustment = calculate_seasonal_temp_adjustment(current_date.month, year_variation_temp) 
            previous_seasonal_temp_adjustment = prev_values[beehive_id]["seasonal_temp_adjustment"]
            smoothed_seasonal_temp_adjustment = exponential_smoothing(previous_seasonal_temp_adjustment, target_seasonal_temp_adjustment, alpha=0.02) 
            prev_values[beehive_id]["seasonal_temp_adjustment"] = smoothed_seasonal_temp_adjustment

            target_seasonal_factor = calculate_seasonal_factor(current_date.month) 
            previous_seasonal_factor = prev_values[beehive_id]["seasonal_factor"]
            smoothed_seasonal_factor = exponential_smoothing(previous_seasonal_factor, target_seasonal_factor, alpha=0.02) 
            prev_values[beehive_id]["seasonal_factor"] = smoothed_seasonal_factor

            target_seasonal_humidity_adjustment = calculate_seasonal_humidity_adjustment(current_date.month, year_variation_humidity) 
            previous_seasonal_humidity_adjustment = prev_values[beehive_id]["seasonal_humidity_adjustment"]
            smoothed_seasonal_humidity_adjustment = exponential_smoothing(previous_seasonal_humidity_adjustment, target_seasonal_humidity_adjustment, alpha=0.02) 
            prev_values[beehive_id]["seasonal_humidity_adjustment"] = smoothed_seasonal_humidity_adjustment

            for hour in range(24): 
                timestamp = datetime.datetime.combine(current_date, datetime.time(hour))
                hour_24h = timestamp.strftime("%H:%M") 

                
                temperature = internal_temp_by_hour(current_date, hour, base_temp_active_hours_year, base_temp_inactive_hours_year, smoothed_seasonal_temp_adjustment=smoothed_seasonal_temp_adjustment, noise_level_temp=noise_level_temp_year) 
                humidity = internal_humidity_by_hour(current_date, hour, base_humidity_active_hours_year, base_humidity_inactive_hours_year, smoothed_seasonal_humidity_adjustment=smoothed_seasonal_humidity_adjustment, noise_level_humidity=noise_level_humidity_year) 

                sound = sound_by_activity() 
                co2 = co2_by_activity() 
                voc = voc_by_activity() 
                sun = sun_exposure(hour) 

                
                if hour == 0: 
                    prev_weight = prev_values[beehive_id]["weight"]
                    current_harvest_date = harvest_dates_year[prev_values[beehive_id]["harvest_index"]]
                    weight, post_harvest_state = weight_by_season_and_harvest( 
                        current_date.month, day_of_month,
                        prev_weight,
                        beehive_factor,
                        harvest_date=current_harvest_date,
                        current_date=current_date,
                        post_harvest=prev_values[beehive_id]["post_harvest"]
                    )
                    prev_values[beehive_id]["weight"] = weight 
                    prev_values[beehive_id]["post_harvest"] = post_harvest_state 
                    prev_values[beehive_id]["min_weight"] = min(prev_values[beehive_id]["min_weight"], weight) 

                    if (current_harvest_date and 
                        current_date.month == current_harvest_date.month and
                        current_date.day == current_harvest_date.day):
                        prev_values[beehive_id]["harvest_index"] = (prev_values[beehive_id]["harvest_index"] + 1) % len(harvest_dates_year) 

                data.append({ 
                    "beehive_id": beehive_id,
                    "timestamp": timestamp,
                    "season_name": season,
                    "hour_24h": hour_24h,
                    "beehive_temperature_c": temperature,
                    "beehive_humidity_percent": humidity,
                    "beehive_weight_kg": prev_values[beehive_id]["weight"],
                    "beehive_sound_db": sound,
                    "co2_ppm": co2,
                    "voc_level": voc,
                    "beehive_sun_exposure": sun
                })

    
    dim_beehive_data.append({
        "beehive_id": beehive_id,
        "beehive_location": beehive_location,
        "initial_weight_kg": round(prev_values[beehive_id]["min_weight"], 2) 
    })


df = pd.DataFrame(data)
dim_beehive_df = pd.DataFrame(dim_beehive_data)


daily_avg = df.groupby([df['timestamp'].dt.date, 'beehive_id']).agg({ 
    'beehive_weight_kg': 'mean',
    'beehive_temperature_c': 'mean',
    'beehive_humidity_percent': 'mean'
}).reset_index()

daily_avg_beehive1 = daily_avg[daily_avg['beehive_id'] == 1] 

fig, axes = plt.subplots(3, 1, figsize=(15, 9)) 

axes[0].plot(daily_avg_beehive1['timestamp'], daily_avg_beehive1['beehive_weight_kg'],
             color='black', label='Average Beehive Weight (kg)') 
axes[0].set_title('Weight, Temperature, and Humidity of Beehives over Time') 
axes[0].set_ylabel('Weight (kg)')
axes[0].grid(True, linestyle='--', alpha=0.5)
axes[0].legend()

axes[1].plot(daily_avg_beehive1['timestamp'], daily_avg_beehive1['beehive_temperature_c'],
             color='red', label='Internal Temperature (°C)') 
axes[1].set_ylabel('Temperature (°C)')
axes[1].grid(True, linestyle='--', alpha=0.5)
axes[1].legend()

axes[2].plot(daily_avg_beehive1['timestamp'], daily_avg_beehive1['beehive_humidity_percent'],
             color='blue', label='Internal Humidity (%)') 
axes[2].set_xlabel('Time')
axes[2].set_ylabel('Humidity (%)')
axes[2].grid(True, linestyle='--', alpha=0.5)
axes[2].legend()

plt.tight_layout()
plt.show()


df.sort_values(by='timestamp').to_csv('fct_beehive.csv', index=False)
dim_beehive_df.to_csv('dim_beehive.csv', index=False)

print("\nData saved to fct_beehive_seasonal_temp.csv and dim_beehive.csv")