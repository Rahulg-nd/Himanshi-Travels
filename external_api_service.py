#!/usr/bin/env python3
"""
External API service for fetching city and location data
Supports international cities using GeoDB Cities API
"""

import requests
import time
from typing import List, Dict, Optional
from functools import lru_cache


class ExternalCityService:
    """Service for fetching city data from external APIs"""
    
    # GeoDB Cities API (free tier: 1000 requests/day)
    GEODB_BASE_URL = "http://geodb-free-service.wirefreethought.com/v1/geo"
    
    # Backup/Alternative APIs (can be added as needed)
    TELEPORT_BASE_URL = "https://api.teleport.org/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HimanshiTravels/1.0',
            'Accept': 'application/json'
        })
        self._last_request_time = 0
        self._rate_limit_delay = 0.1  # 100ms between requests
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - time_since_last)
        self._last_request_time = time.time()
    
    @lru_cache(maxsize=1000)
    def get_city_suggestions(self, query: str, limit: int = 10, country_filter: str = None) -> List[Dict]:
        """
        Get city suggestions from GeoDB Cities API
        Returns list of cities with name, country, and region info
        Enhanced with better filtering and country support
        """
        if not query or len(query) < 2:
            return []
        
        try:
            self._rate_limit()
            
            # GeoDB Cities API endpoint for city search
            url = f"{self.GEODB_BASE_URL}/cities"
            params = {
                'namePrefix': query,
                'limit': min(limit * 2, 20),  # Get more results for better filtering
                'sort': 'name'
            }
            
            # Add country filter if provided
            if country_filter:
                params['countryIds'] = self._get_country_code(country_filter)
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            if 'data' in data:
                for city_data in data['data']:
                    # Enhanced filtering based on query
                    city_name = city_data.get('name', '').lower()
                    query_lower = query.lower()
                    
                    # Score cities based on how well they match
                    score = self._calculate_match_score(city_name, query_lower)
                    
                    suggestion = {
                        'name': city_data.get('name', ''),
                        'country': city_data.get('country', ''),
                        'region': city_data.get('region', ''),
                        'display': self._format_city_display(city_data),
                        'type': 'city',
                        'population': city_data.get('population', 0),
                        'latitude': city_data.get('latitude'),
                        'longitude': city_data.get('longitude'),
                        'match_score': score
                    }
                    suggestions.append(suggestion)
            
            # Sort by match score (higher is better) and population
            suggestions.sort(key=lambda x: (x['match_score'], x['population']), reverse=True)
            
            return suggestions[:limit]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cities from GeoDB API: {e}")
            # Fallback to local data if API fails
            return self._get_fallback_city_suggestions(query, limit, country_filter)
        except Exception as e:
            print(f"Unexpected error in city search: {e}")
            return self._get_fallback_city_suggestions(query, limit, country_filter)
    
    def _calculate_match_score(self, city_name: str, query: str) -> int:
        """Calculate how well a city name matches the query"""
        if city_name == query:
            return 100  # Exact match
        elif city_name.startswith(query):
            return 90   # Starts with query
        elif query in city_name:
            return 80   # Contains query
        else:
            return 50   # Default score
    
    def _get_country_code(self, country_name: str) -> str:
        """Get country code for API filtering"""
        country_codes = {
            'india': 'IN',
            'united states': 'US',
            'usa': 'US',
            'united kingdom': 'GB',
            'uk': 'GB',
            'france': 'FR',
            'germany': 'DE',
            'japan': 'JP',
            'australia': 'AU',
            'canada': 'CA',
            'singapore': 'SG',
            'uae': 'AE',
            'united arab emirates': 'AE',
            'thailand': 'TH',
            'malaysia': 'MY',
            'spain': 'ES',
            'italy': 'IT',
            'netherlands': 'NL',
            'south korea': 'KR'
        }
        return country_codes.get(country_name.lower(), '')
    
    def get_country_suggestions(self, query: str, limit: int = 10) -> List[Dict]:
        """Get country suggestions for autocomplete"""
        countries = [
            {'name': 'India', 'code': 'IN', 'popular': True},
            {'name': 'United States', 'code': 'US', 'popular': True},
            {'name': 'United Kingdom', 'code': 'GB', 'popular': True},
            {'name': 'France', 'code': 'FR', 'popular': True},
            {'name': 'Germany', 'code': 'DE', 'popular': True},
            {'name': 'Japan', 'code': 'JP', 'popular': True},
            {'name': 'Australia', 'code': 'AU', 'popular': True},
            {'name': 'Canada', 'code': 'CA', 'popular': True},
            {'name': 'Singapore', 'code': 'SG', 'popular': True},
            {'name': 'United Arab Emirates', 'code': 'AE', 'popular': True},
            {'name': 'Thailand', 'code': 'TH', 'popular': True},
            {'name': 'Malaysia', 'code': 'MY', 'popular': True},
            {'name': 'Spain', 'code': 'ES', 'popular': True},
            {'name': 'Italy', 'code': 'IT', 'popular': True},
            {'name': 'Netherlands', 'code': 'NL', 'popular': True},
            {'name': 'South Korea', 'code': 'KR', 'popular': True},
            {'name': 'China', 'code': 'CN', 'popular': True},
            {'name': 'Brazil', 'code': 'BR', 'popular': True},
            {'name': 'Russia', 'code': 'RU', 'popular': True},
            {'name': 'Turkey', 'code': 'TR', 'popular': True},
        ]
        
        if not query or len(query) < 1:
            return countries[:limit]
        
        query_lower = query.lower()
        filtered = [
            country for country in countries 
            if query_lower in country['name'].lower()
        ]
        
        return filtered[:limit]
    
    def _format_city_display(self, city_data: Dict) -> str:
        """Format city display string"""
        name = city_data.get('name', '')
        region = city_data.get('region', '')
        country = city_data.get('country', '')
        
        if region and region != name:
            return f"{name}, {region}, {country}"
        else:
            return f"{name}, {country}"
    
    def _get_fallback_city_suggestions(self, query: str, limit: int = 10, country_filter: str = None) -> List[Dict]:
        """Fallback to hardcoded popular international and comprehensive Indian cities if API fails"""
        fallback_cities = [
            # International cities
            {"name": "New York", "country": "United States", "region": "New York", "type": "city"},
            {"name": "London", "country": "United Kingdom", "region": "England", "type": "city"},
            {"name": "Paris", "country": "France", "region": "Île-de-France", "type": "city"},
            {"name": "Tokyo", "country": "Japan", "region": "Tokyo", "type": "city"},
            {"name": "Dubai", "country": "United Arab Emirates", "region": "Dubai", "type": "city"},
            {"name": "Singapore", "country": "Singapore", "region": "Singapore", "type": "city"},
            {"name": "Sydney", "country": "Australia", "region": "New South Wales", "type": "city"},
            {"name": "Bangkok", "country": "Thailand", "region": "Bangkok", "type": "city"},
            {"name": "Istanbul", "country": "Turkey", "region": "Istanbul", "type": "city"},
            {"name": "Rome", "country": "Italy", "region": "Lazio", "type": "city"},
            {"name": "Barcelona", "country": "Spain", "region": "Catalonia", "type": "city"},
            {"name": "Amsterdam", "country": "Netherlands", "region": "North Holland", "type": "city"},
            {"name": "Seoul", "country": "South Korea", "region": "Seoul", "type": "city"},
            {"name": "Hong Kong", "country": "Hong Kong", "region": "Hong Kong", "type": "city"},
            {"name": "Kuala Lumpur", "country": "Malaysia", "region": "Kuala Lumpur", "type": "city"},
            
            # Comprehensive Indian cities - Tier 1
            {"name": "Mumbai", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Delhi", "country": "India", "region": "Delhi", "type": "city"},
            {"name": "Bangalore", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Bengaluru", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Chennai", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Kolkata", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Hyderabad", "country": "India", "region": "Telangana", "type": "city"},
            {"name": "Pune", "country": "India", "region": "Maharashtra", "type": "city"},
            
            # Tier 2 Indian cities
            {"name": "Jaipur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Ahmedabad", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Surat", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Lucknow", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Kanpur", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Nagpur", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Indore", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Thane", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Bhopal", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Visakhapatnam", "country": "India", "region": "Andhra Pradesh", "type": "city"},
            {"name": "Patna", "country": "India", "region": "Bihar", "type": "city"},
            {"name": "Vadodara", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Ghaziabad", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Ludhiana", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Agra", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Nashik", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Faridabad", "country": "India", "region": "Haryana", "type": "city"},
            {"name": "Meerut", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Rajkot", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Kalyan-Dombivli", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Vasai-Virar", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Varanasi", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Srinagar", "country": "India", "region": "Jammu and Kashmir", "type": "city"},
            {"name": "Aurangabad", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Dhanbad", "country": "India", "region": "Jharkhand", "type": "city"},
            {"name": "Amritsar", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Navi Mumbai", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Allahabad", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Prayagraj", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Howrah", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Ranchi", "country": "India", "region": "Jharkhand", "type": "city"},
            {"name": "Jabalpur", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Gwalior", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Coimbatore", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Vijayawada", "country": "India", "region": "Andhra Pradesh", "type": "city"},
            {"name": "Jodhpur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Madurai", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Raipur", "country": "India", "region": "Chhattisgarh", "type": "city"},
            {"name": "Kota", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Guwahati", "country": "India", "region": "Assam", "type": "city"},
            {"name": "Chandigarh", "country": "India", "region": "Chandigarh", "type": "city"},
            {"name": "Thiruvananthapuram", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Solapur", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Hubballi-Dharwad", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Tiruchirappalli", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Bareilly", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Mysore", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Tiruppur", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Gurgaon", "country": "India", "region": "Haryana", "type": "city"},
            {"name": "Gurugram", "country": "India", "region": "Haryana", "type": "city"},
            {"name": "Aligarh", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Jalandhar", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Abohar", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Bathinda", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Mohali", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Patiala", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Pathankot", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Hoshiarpur", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Batala", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Moga", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Malerkotla", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Khanna", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Phagwara", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Muktsar", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Barnala", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Faridkot", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Kapurthala", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Sangrur", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Firozpur", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Sunam", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Malout", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Nabha", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Tarn Taran", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Jagraon", "country": "India", "region": "Punjab", "type": "city"},
            {"name": "Bhubaneswar", "country": "India", "region": "Odisha", "type": "city"},
            {"name": "Salem", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Warangal", "country": "India", "region": "Telangana", "type": "city"},
            {"name": "Guntur", "country": "India", "region": "Andhra Pradesh", "type": "city"},
            {"name": "Bhiwandi", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Saharanpur", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Gorakhpur", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Bikaner", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Amravati", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Noida", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Jamshedpur", "country": "India", "region": "Jharkhand", "type": "city"},
            {"name": "Bhilai", "country": "India", "region": "Chhattisgarh", "type": "city"},
            {"name": "Cuttack", "country": "India", "region": "Odisha", "type": "city"},
            {"name": "Firozabad", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Kochi", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Nellore", "country": "India", "region": "Andhra Pradesh", "type": "city"},
            {"name": "Bhavnagar", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Dehradun", "country": "India", "region": "Uttarakhand", "type": "city"},
            {"name": "Durgapur", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Asansol", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Rourkela", "country": "India", "region": "Odisha", "type": "city"},
            {"name": "Nanded", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Kolhapur", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Ajmer", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Akola", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Gulbarga", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Jamnagar", "country": "India", "region": "Gujarat", "type": "city"},
            {"name": "Ujjain", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Loni", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Siliguri", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Jhansi", "country": "India", "region": "Uttar Pradesh", "type": "city"},
            {"name": "Ulhasnagar", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Jammu", "country": "India", "region": "Jammu and Kashmir", "type": "city"},
            {"name": "Sangli-Miraj & Kupwad", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Mangalore", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Erode", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Belgaum", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Ambattur", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Tirunelveli", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Malegaon", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Gaya", "country": "India", "region": "Bihar", "type": "city"},
            {"name": "Jalgaon", "country": "India", "region": "Maharashtra", "type": "city"},
            {"name": "Udaipur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Maheshtala", "country": "India", "region": "West Bengal", "type": "city"},
            
            # Tier 3 Indian cities including Sri Ganganagar and other important ones
            {"name": "Sri Ganganagar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Ganganagar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Hanumangarh", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Sikar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Alwar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Bharatpur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Pali", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Bhilwara", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Tonk", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Kishangarh", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Beawar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Churu", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Jhunjhunu", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Sawai Madhopur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Nagaur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Makrana", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Sujangarh", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Ladnun", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Didwana", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Ratangarh", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Sardarshahar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Suratgarh", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Padampur", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Raisinghnagar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Anupgarh", "country": "India", "region": "Rajasthan", "type": "city"},
            
            # Tourism and travel important cities
            {"name": "Goa", "country": "India", "region": "Goa", "type": "city"},
            {"name": "Panaji", "country": "India", "region": "Goa", "type": "city"},
            {"name": "Margao", "country": "India", "region": "Goa", "type": "city"},
            {"name": "Rishikesh", "country": "India", "region": "Uttarakhand", "type": "city"},
            {"name": "Haridwar", "country": "India", "region": "Uttarakhand", "type": "city"},
            {"name": "Dharamshala", "country": "India", "region": "Himachal Pradesh", "type": "city"},
            {"name": "Manali", "country": "India", "region": "Himachal Pradesh", "type": "city"},
            {"name": "Shimla", "country": "India", "region": "Himachal Pradesh", "type": "city"},
            {"name": "Mussoorie", "country": "India", "region": "Uttarakhand", "type": "city"},
            {"name": "Nainital", "country": "India", "region": "Uttarakhand", "type": "city"},
            {"name": "Mount Abu", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Pushkar", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Jaisalmer", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Ranthambore", "country": "India", "region": "Rajasthan", "type": "city"},
            {"name": "Khajuraho", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Orchha", "country": "India", "region": "Madhya Pradesh", "type": "city"},
            {"name": "Hampi", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Badami", "country": "India", "region": "Karnataka", "type": "city"},
            {"name": "Munnar", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Alleppey", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Kumarakom", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Varkala", "country": "India", "region": "Kerala", "type": "city"},
            {"name": "Kodaikanal", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Ooty", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Pondicherry", "country": "India", "region": "Puducherry", "type": "city"},
            {"name": "Puducherry", "country": "India", "region": "Puducherry", "type": "city"},
            {"name": "Mahabalipuram", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Kanyakumari", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Rameshwaram", "country": "India", "region": "Tamil Nadu", "type": "city"},
            {"name": "Darjeeling", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Kalimpong", "country": "India", "region": "West Bengal", "type": "city"},
            {"name": "Gangtok", "country": "India", "region": "Sikkim", "type": "city"},
            {"name": "Shillong", "country": "India", "region": "Meghalaya", "type": "city"},
            {"name": "Kohima", "country": "India", "region": "Nagaland", "type": "city"},
            {"name": "Imphal", "country": "India", "region": "Manipur", "type": "city"},
            {"name": "Aizawl", "country": "India", "region": "Mizoram", "type": "city"},
            {"name": "Agartala", "country": "India", "region": "Tripura", "type": "city"},
            {"name": "Itanagar", "country": "India", "region": "Arunachal Pradesh", "type": "city"},
            {"name": "Leh", "country": "India", "region": "Ladakh", "type": "city"},
            {"name": "Kargil", "country": "India", "region": "Ladakh", "type": "city"},
            {"name": "Port Blair", "country": "India", "region": "Andaman and Nicobar Islands", "type": "city"},
        ]
        
        query_lower = query.lower()
        suggestions = []
        
        for city in fallback_cities:
            # Filter by country if specified
            if country_filter and country_filter.lower() not in city["country"].lower():
                continue
                
            # Calculate match score for better sorting
            match_score = self._calculate_match_score(city["name"].lower(), query_lower)
            
            if (query_lower in city["name"].lower() or 
                city["name"].lower().startswith(query_lower) or
                query_lower in city["country"].lower()):
                suggestions.append({
                    **city,
                    "display": f"{city['name']}, {city['region']}, {city['country']}",
                    "match_score": match_score
                })
        
        # Sort by match score
        suggestions.sort(key=lambda x: x['match_score'], reverse=True)
        return suggestions[:limit]
    
    @lru_cache(maxsize=100)
    def get_hotel_area_suggestions(self, city: str) -> List[str]:
        """
        Get hotel area suggestions for a city
        For now, returns generic area types that apply to most cities
        Could be enhanced with city-specific data from external APIs
        """
        generic_areas = [
            "City Center",
            "Business District",
            "Airport Area",
            "Railway Station Area",
            "Tourist District",
            "Beach Area",
            "Shopping District",
            "Old Town",
            "Downtown",
            "Suburbs"
        ]
        
        # Add city-specific areas for major destinations
        city_specific_areas = {
            "mumbai": ["Colaba", "Bandra", "Juhu", "Andheri", "Powai", "BKC"],
            "delhi": ["Connaught Place", "Karol Bagh", "Paharganj", "Aerocity", "Gurgaon"],
            "bangalore": ["Whitefield", "Koramangala", "Indiranagar", "Electronic City", "MG Road"],
            "goa": ["North Goa", "South Goa", "Panaji", "Calangute", "Baga"],
            "jaipur": ["Pink City", "Civil Lines", "Malviya Nagar", "Vaishali Nagar"],
            "london": ["Westminster", "Covent Garden", "Camden", "Shoreditch", "Kensington"],
            "paris": ["Champs-Élysées", "Marais", "Saint-Germain", "Montmartre", "Louvre"],
            "new york": ["Manhattan", "Brooklyn", "Times Square", "Central Park", "Financial District"],
            "dubai": ["Downtown", "Marina", "JBR", "Deira", "Bur Dubai"],
            "bangkok": ["Sukhumvit", "Silom", "Khao San Road", "Siam", "Chatuchak"],
        }
        
        city_lower = city.lower()
        specific_areas = city_specific_areas.get(city_lower, [])
        
        return specific_areas + generic_areas[:6]  # Limit to avoid overwhelming users
    
    @lru_cache(maxsize=10)
    def get_popular_routes(self) -> List[Dict]:
        """Get popular travel routes (mix of domestic and international)"""
        return [
            # Domestic Indian routes
            {"from": "Mumbai", "to": "Pune"},
            {"from": "Delhi", "to": "Jaipur"},
            {"from": "Delhi", "to": "Agra"},
            {"from": "Mumbai", "to": "Goa"},
            {"from": "Bangalore", "to": "Mysore"},
            {"from": "Chennai", "to": "Pondicherry"},
            {"from": "Delhi", "to": "Shimla"},
            {"from": "Delhi", "to": "Manali"},
            {"from": "Kochi", "to": "Munnar"},
            {"from": "Jaipur", "to": "Udaipur"},
            
            # Popular international routes
            {"from": "Mumbai", "to": "Dubai"},
            {"from": "Delhi", "to": "London"},
            {"from": "Bangalore", "to": "Singapore"},
            {"from": "Mumbai", "to": "New York"},
            {"from": "Delhi", "to": "Paris"},
            {"from": "Chennai", "to": "Bangkok"},
            {"from": "Delhi", "to": "Tokyo"},
            {"from": "Mumbai", "to": "Sydney"},
            {"from": "Bangalore", "to": "San Francisco"},
            {"from": "Delhi", "to": "Frankfurt"},
            
            # Regional international routes
            {"from": "Bangkok", "to": "Phuket"},
            {"from": "London", "to": "Paris"},
            {"from": "New York", "to": "Los Angeles"},
            {"from": "Dubai", "to": "Istanbul"},
            {"from": "Singapore", "to": "Kuala Lumpur"},
        ]


# Global instance
external_city_service = ExternalCityService()


def get_city_suggestions(query: str, limit: int = 10, country_filter: str = None) -> List[Dict]:
    """Wrapper function for compatibility with existing code"""
    return external_city_service.get_city_suggestions(query, limit, country_filter)


def get_country_suggestions(query: str, limit: int = 10) -> List[Dict]:
    """Wrapper function for country suggestions"""
    return external_city_service.get_country_suggestions(query, limit)


def get_hotel_area_suggestions(city: str) -> List[str]:
    """Wrapper function for compatibility with existing code"""
    return external_city_service.get_hotel_area_suggestions(city)


def get_popular_routes() -> List[Dict]:
    """Wrapper function for compatibility with existing code"""
    return external_city_service.get_popular_routes()


if __name__ == "__main__":
    # Test the service
    print("Testing External City Service...")
    
    # Test city suggestions
    cities = get_city_suggestions("Mumbai", 5)
    print(f"Cities for 'Mumbai': {cities}")
    
    cities = get_city_suggestions("London", 5)
    print(f"Cities for 'London': {cities}")
    
    # Test hotel areas
    areas = get_hotel_area_suggestions("Mumbai")
    print(f"Hotel areas for Mumbai: {areas}")
    
    # Test popular routes
    routes = get_popular_routes()
    print(f"Popular routes: {routes[:5]}")
