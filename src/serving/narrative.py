class NarrativeService:
    @staticmethod
    def generate_briefing(current_pm25, risk_level, forecast_trend):
        """
        Generates a high-level daily briefing string.
        """
        story = f"Air quality is currently classified as {risk_level}. "
        
        if risk_level == "Safe":
            story += "Conditions are optimal for outdoor activities. "
        elif risk_level == "Moderate":
            story += "Sensitive individuals should consider limiting prolonged outdoor exertion. "
        else:
            story += "Health warnings are in effect. Please stay indoors and use air purification if possible. "
            
        if forecast_trend > 0:
            story += "Models predict a slight deterioration over the next 24 hours."
        else:
            story += "Conditions are expected to improve throughout the day."
            
        return story

    @staticmethod
    def generate_detailed_insight(pm25, pm10, no2, o3):
        """
        Generates a technical breakdown.
        """
        dominant = max(pm25, pm10, no2, o3)
        pollutant = "PM2.5"
        if dominant == pm10: pollutant = "PM10"
        elif dominant == no2: pollutant = "NO2"
        elif dominant == o3: pollutant = "Ozone"
        
        return f"The primary driver of current AQI levels is {pollutant} ({dominant:.1f} µg/m³). This is often associated with vehicle emissions and industrial activity."
