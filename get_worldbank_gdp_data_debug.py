import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient
import json
from datetime import datetime

# Initialize API client
client = ApiClient()

# Fetch GDP data for Brazil from World Bank
indicator_code = "NY.GDP.MKTP.CD"  # GDP (current US$)
country_code = "BRA" # Brazil

print(f"Fetching GDP data for {country_code} (Indicator: {indicator_code})")
try:
    gdp_raw_data = client.call_api("DataBank/indicator_data", query={"indicator": indicator_code, "country": country_code})
    print("Raw GDP data received:", json.dumps(gdp_raw_data, indent=4)) # Print raw response for debugging
except Exception as e:
    print(f"Error calling DataBank API: {e}")
    gdp_raw_data = None

processed_gdp_data = []
if gdp_raw_data and gdp_raw_data.get("data"):
    country_name = gdp_raw_data.get("countryName")
    indicator_name = gdp_raw_data.get("indicatorName")
    print(f"Processing data for {country_name} - {indicator_name}")
    
    for year_str, value in gdp_raw_data["data"].items():
        if value is not None: # Only include years with actual data
            try:
                year = int(year_str)
                # Create a date string for the end of the year, e.g., YYYY-12-31
                # This helps in treating it like other time series data
                date_obj = datetime(year, 12, 31)
                date_referencia = date_obj.strftime("%Y-%m-%d")
                processed_gdp_data.append({
                    "data_referencia": date_referencia,
                    "valor": float(value) # Ensure value is float
                })
            except ValueError:
                print(f"Skipping invalid year format: {year_str}")
                continue
    
    # Sort data by date just in case it's not
    processed_gdp_data.sort(key=lambda x: x["data_referencia"])
    print(f"Successfully processed {len(processed_gdp_data)} GDP data points.")
else:
    print("No GDP data found or error in API response structure based on 'gdp_raw_data.get(\'data\')'.")

# Save processed data to a JSON file
output_file = "gdp_data.json"
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_gdp_data, f, ensure_ascii=False, indent=4)
    print(f"GDP data (even if empty) successfully saved to {output_file}")
except IOError as e:
    print(f"Error writing GDP data to JSON file: {e}")

