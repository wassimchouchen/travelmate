from crewai import Task
from textwrap import dedent
from datetime import date

class TripTasks:
    def identify_task(self, agent, origin, cities, interests, range):
        return Task(
            description=dedent(f"""
                Your task is to perform a comprehensive analysis and select the optimal city for travel.
                Follow these steps IN ORDER:

                1. FIRST, conduct detailed weather and seasonal analysis for: {cities}
                2. THEN, perform comprehensive travel cost research from {origin}
                3. FINALLY, identify and evaluate attractions and experiences

                REQUIRED FORMAT FOR FINAL ANSWER:
                ---
                Selected City: [city name]

                Weather Analysis:
                - Current weather patterns and forecasts
                - Seasonal events and festivals
                - Best time of day for outdoor activities
                - Potential weather-related concerns

                Travel Logistics:
                - Flight options and estimated costs from {origin}
                - Alternative transportation methods (train, bus, etc.)
                - Visa requirements and processing time
                - Travel insurance recommendations
                - Required vaccinations or health precautions

                Accommodation Options:
                - Luxury hotels (price range, notable properties)
                - Mid-range hotels (price range, recommended areas)
                - Budget accommodations (hostels, guesthouses)
                - Unique stays (boutique hotels, local experiences)
                - Best neighborhoods for tourists

                Key Attractions:
                - Major historical sites and monuments
                - Museums and cultural institutions
                - Natural attractions and parks
                - Activities matching interests: {interests}
                - Seasonal special events
                - Popular local experiences

                Local Considerations:
                - Language considerations
                - Cultural etiquette
                - Safety information
                - Local transportation options
                - Currency and payment methods
                
                Trip Timing: {range}
                ---

                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="Comprehensive city analysis with detailed weather, travel logistics, accommodations, attractions, and local considerations"
        )

    def gather_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                Create a detailed local expert guide for the selected city.
                Follow these steps IN ORDER:

                1. FIRST, research authentic local experiences
                2. THEN, compile cultural and practical information
                3. FINALLY, create specific recommendations

                REQUIRED FORMAT FOR FINAL ANSWER:
                ---
                Local's Guide to [City Name]

                Hidden Gems:
                - [List 5-7 unique local spots with specific details]
                - Best times to visit each location
                - How to get there
                - Estimated costs
                - Local tips for each spot

                Cultural Insights:
                - Local customs and traditions
                - Dining etiquette
                - Appropriate dress codes
                - Common phrases in local language
                - Social norms and taboos
                - Religious considerations
                - Business hours and siesta times

                Food & Dining:
                - Must-try local dishes
                - Best local restaurants by price range
                - Street food recommendations
                - Food markets and timing
                - Dietary restriction considerations
                - Tipping customs

                Local Transportation:
                - Public transit options and costs
                - Taxi/ride-share services and apps
                - Walking routes and areas
                - Bike rental information
                - Transport apps to download

                Shopping Guide:
                - Local markets and timing
                - Authentic souvenir shops
                - Artisan workshops
                - Price negotiation customs
                - Shopping districts by interest

                Entertainment:
                - Live music venues
                - Theater and performance spaces
                - Nightlife areas
                - Local festivals and events
                - Sports and recreation

                Practical Tips:
                - Emergency contacts
                - Healthcare facilities
                - WiFi availability
                - Mobile service providers
                - Banking and ATM locations
                - Best photo spots
                - Local apps to download

                For Travelers From: {origin}
                Visiting In: {range}
                Interests: {interests}
                ---

                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="Comprehensive local guide with detailed recommendations and practical information"
        )

    def plan_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                Create a detailed 7-day travel itinerary with all necessary information.
                Follow these steps IN ORDER:

                1. FIRST, plan comprehensive daily activities
                2. THEN, add specific venues and logistics
                3. FINALLY, include detailed costs and preparations

                REQUIRED FORMAT FOR FINAL ANSWER:
                ---
                7-Day Itinerary in [City Name]

                Pre-Trip Preparation:
                - Visa requirements and timeline
                - Recommended vaccinations
                - Travel insurance options
                - Required bookings and reservations
                - Mobile apps to download

                Travel Details:
                - Flight options and booking recommendations
                - Airport transfer information
                - Hotel check-in/out times
                - Local transportation passes

                Day 1:
                - Morning: [specific venue/activity]
                  * Opening hours
                  * Admission costs
                  * Transportation details
                  * Recommended duration
                  * Food options nearby
                - Afternoon: [specific venue/activity]
                  * [Same details as above]
                - Evening: [specific venue/activity]
                  * [Same details as above]
                [Continue for all 7 days]

                Packing List:
                - Essential clothing (based on {range} weather)
                - Electronics and adapters
                - Travel documents
                - Health and safety items
                - Specialized gear for activities

                Budget Breakdown:
                - Flights and transportation
                - Accommodation costs
                - Daily food expenses
                - Activity and entrance fees
                - Shopping allowance
                - Emergency fund
                - Total estimate with breakdown

                Contingency Plans:
                - Rainy day alternatives
                - Backup activities
                - Emergency contacts
                - Travel insurance details
                - Embassy information

                For: Traveler from {origin}
                Interests: {interests}
                Special Considerations: [dietary, accessibility, etc.]
                ---

                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="Comprehensive 7-day itinerary with specific venues, costs, and contingency plans"
        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"
