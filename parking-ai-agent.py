import datetime
import random
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

class VehicleType(Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    HANDICAPPED = "handicapped"

class ParkingSpotType(Enum):
    REGULAR = "regular"
    COMPACT = "compact"
    LARGE = "large"
    HANDICAPPED = "handicapped"
    MOTORCYCLE = "motorcycle"

class ParkingSpot:
    def __init__(self, spot_id: str, spot_type: ParkingSpotType, level: int, section: str):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.level = level
        self.section = section
        self.is_occupied = False
        self.vehicle_id = None
        self.occupied_since = None

    def occupy(self, vehicle_id: str) -> bool:
        if not self.is_occupied:
            self.is_occupied = True
            self.vehicle_id = vehicle_id
            self.occupied_since = datetime.datetime.now()
            return True
        return False

    def vacate(self) -> Optional[Tuple[str, datetime.datetime]]:
        if self.is_occupied:
            vehicle_id = self.vehicle_id
            occupied_since = self.occupied_since
            self.is_occupied = False
            self.vehicle_id = None
            self.occupied_since = None
            return (vehicle_id, occupied_since)
        return None

    def __str__(self) -> str:
        status = "Occupied" if self.is_occupied else "Available"
        return f"Spot {self.spot_id} ({self.spot_type.value}) - {status}"

class Vehicle:
    def __init__(self, vehicle_id: str, vehicle_type: VehicleType, license_plate: str):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.license_plate = license_plate
        self.entry_time = None
        self.exit_time = None
        self.parked_spot_id = None

    def __str__(self) -> str:
        return f"{self.vehicle_type.value.title()} (Plate: {self.license_plate})"

class ParkingRate:
    def __init__(self, vehicle_type: VehicleType, hourly_rate: float, daily_max: float):
        self.vehicle_type = vehicle_type
        self.hourly_rate = hourly_rate
        self.daily_max = daily_max

class ParkingTicket:
    def __init__(self, ticket_id: str, vehicle_id: str, entry_time: datetime.datetime):
        self.ticket_id = ticket_id
        self.vehicle_id = vehicle_id
        self.entry_time = entry_time
        self.payment_time = None
        self.amount_paid = 0.0
        self.is_paid = False
        self.exit_time = None

    def pay(self, amount: float) -> bool:
        if not self.is_paid:
            self.amount_paid = amount
            self.payment_time = datetime.datetime.now()
            self.is_paid = True
            return True
        return False

    def complete_exit(self) -> bool:
        if self.is_paid:
            self.exit_time = datetime.datetime.now()
            return True
        return False

class ParkingAI:
    def __init__(self):
        self.spots: Dict[str, ParkingSpot] = {}
        self.vehicles: Dict[str, Vehicle] = {}
        self.tickets: Dict[str, ParkingTicket] = {}
        self.parking_rates: Dict[VehicleType, ParkingRate] = {}
        self.total_revenue = 0.0
        self.occupancy_history = []  # Store occupancy snapshots
        
        # Initialize rates
        self._initialize_rates()

    def _initialize_rates(self):
        self.parking_rates[VehicleType.CAR] = ParkingRate(VehicleType.CAR, 2.0, 24.0)
        self.parking_rates[VehicleType.MOTORCYCLE] = ParkingRate(VehicleType.MOTORCYCLE, 1.0, 12.0)
        self.parking_rates[VehicleType.TRUCK] = ParkingRate(VehicleType.TRUCK, 4.0, 48.0)
        self.parking_rates[VehicleType.HANDICAPPED] = ParkingRate(VehicleType.HANDICAPPED, 1.0, 12.0)

    def initialize_parking_lot(self, levels: int, spots_per_level: int):
        """Initialize the parking lot with a given number of levels and spots per level"""
        spot_id_counter = 1
        for level in range(1, levels + 1):
            # Define sections A, B, C, D for each level
            sections = ["A", "B", "C", "D"]
            
            for section in sections:
                # Allocate different types of spots in each section
                spots_in_section = spots_per_level // len(sections)
                
                # Define distribution of spot types (can be customized)
                regular_spots = int(spots_in_section * 0.6)
                compact_spots = int(spots_in_section * 0.2)
                large_spots = int(spots_in_section * 0.1)
                handicapped_spots = int(spots_in_section * 0.05)
                motorcycle_spots = spots_in_section - regular_spots - compact_spots - large_spots - handicapped_spots
                
                # Create regular spots
                for i in range(regular_spots):
                    spot_id = f"{level}-{section}-{spot_id_counter}"
                    self.spots[spot_id] = ParkingSpot(spot_id, ParkingSpotType.REGULAR, level, section)
                    spot_id_counter += 1
                
                # Create compact spots
                for i in range(compact_spots):
                    spot_id = f"{level}-{section}-{spot_id_counter}"
                    self.spots[spot_id] = ParkingSpot(spot_id, ParkingSpotType.COMPACT, level, section)
                    spot_id_counter += 1
                
                # Create large spots
                for i in range(large_spots):
                    spot_id = f"{level}-{section}-{spot_id_counter}"
                    self.spots[spot_id] = ParkingSpot(spot_id, ParkingSpotType.LARGE, level, section)
                    spot_id_counter += 1
                
                # Create handicapped spots
                for i in range(handicapped_spots):
                    spot_id = f"{level}-{section}-{spot_id_counter}"
                    self.spots[spot_id] = ParkingSpot(spot_id, ParkingSpotType.HANDICAPPED, level, section)
                    spot_id_counter += 1
                
                # Create motorcycle spots
                for i in range(motorcycle_spots):
                    spot_id = f"{level}-{section}-{spot_id_counter}"
                    self.spots[spot_id] = ParkingSpot(spot_id, ParkingSpotType.MOTORCYCLE, level, section)
                    spot_id_counter += 1
        
        print(f"Parking lot initialized with {len(self.spots)} spots across {levels} levels")

    def find_available_spot(self, vehicle_type: VehicleType) -> Optional[str]:
        """Find an available parking spot suitable for the given vehicle type"""
        available_spots = []
        
        # Define which spot types are suitable for each vehicle type
        suitable_spot_types = {
            VehicleType.CAR: [ParkingSpotType.REGULAR, ParkingSpotType.LARGE],
            VehicleType.MOTORCYCLE: [ParkingSpotType.MOTORCYCLE, ParkingSpotType.REGULAR, ParkingSpotType.LARGE],
            VehicleType.TRUCK: [ParkingSpotType.LARGE],
            VehicleType.HANDICAPPED: [ParkingSpotType.HANDICAPPED, ParkingSpotType.LARGE]
        }
        
        # First check for exact type match - optimal allocation
        primary_spots = []
        secondary_spots = []
        
        for spot_id, spot in self.spots.items():
            if not spot.is_occupied:
                # Primary match (exact type match)
                if (vehicle_type == VehicleType.CAR and spot.spot_type == ParkingSpotType.REGULAR) or \
                   (vehicle_type == VehicleType.MOTORCYCLE and spot.spot_type == ParkingSpotType.MOTORCYCLE) or \
                   (vehicle_type == VehicleType.TRUCK and spot.spot_type == ParkingSpotType.LARGE) or \
                   (vehicle_type == VehicleType.HANDICAPPED and spot.spot_type == ParkingSpotType.HANDICAPPED):
                    primary_spots.append(spot_id)
                # Secondary match (suitable but not optimal)
                elif spot.spot_type in suitable_spot_types[vehicle_type]:
                    secondary_spots.append(spot_id)
        
        # Prefer exact matches, then suitable spots
        if primary_spots:
            # Find closest to entrance (for simplicity, we'll use lower level and section A as closest)
            primary_spots.sort(key=lambda x: (int(x.split('-')[0]), x.split('-')[1]))
            return primary_spots[0]
        elif secondary_spots:
            secondary_spots.sort(key=lambda x: (int(x.split('-')[0]), x.split('-')[1]))
            return secondary_spots[0]
        
        return None

    def vehicle_entry(self, license_plate: str, vehicle_type: VehicleType) -> Optional[Tuple[str, str]]:
        """Handle vehicle entry - find a spot, generate ticket, and return spot location and ticket"""
        # Create a vehicle record
        vehicle_id = f"V-{len(self.vehicles) + 1}"
        vehicle = Vehicle(vehicle_id, vehicle_type, license_plate)
        vehicle.entry_time = datetime.datetime.now()
        
        # Find a suitable parking spot
        spot_id = self.find_available_spot(vehicle_type)
        if not spot_id:
            return None  # No available spots
        
        # Park the vehicle
        spot = self.spots[spot_id]
        spot.occupy(vehicle_id)
        vehicle.parked_spot_id = spot_id
        
        # Create a ticket
        ticket_id = f"T-{len(self.tickets) + 1}"
        ticket = ParkingTicket(ticket_id, vehicle_id, vehicle.entry_time)
        
        # Save records
        self.vehicles[vehicle_id] = vehicle
        self.tickets[ticket_id] = ticket
        
        # Return the spot location and ticket ID
        location_info = f"Level {spot.level}, Section {spot.section}, Spot {spot.spot_id}"
        return (location_info, ticket_id)

    def calculate_parking_fee(self, ticket_id: str) -> float:
        """Calculate the parking fee for a given ticket"""
        if ticket_id not in self.tickets:
            return 0.0
        
        ticket = self.tickets[ticket_id]
        vehicle = self.vehicles[ticket.vehicle_id]
        rate = self.parking_rates[vehicle.vehicle_type]
        
        current_time = datetime.datetime.now()
        duration = current_time - ticket.entry_time
        hours = duration.total_seconds() / 3600
        
        # Calculate fee
        fee = hours * rate.hourly_rate
        
        # Apply daily maximum if applicable
        days = hours / 24
        daily_max_fee = days * rate.daily_max
        
        return min(fee, daily_max_fee)

    def pay_ticket(self, ticket_id: str) -> Tuple[bool, float]:
        """Process payment for a parking ticket"""
        if ticket_id not in self.tickets:
            return (False, 0.0)
        
        ticket = self.tickets[ticket_id]
        if ticket.is_paid:
            return (False, 0.0)
        
        fee = self.calculate_parking_fee(ticket_id)
        payment_success = ticket.pay(fee)
        
        if payment_success:
            self.total_revenue += fee
            return (True, fee)
        
        return (False, 0.0)

    def vehicle_exit(self, ticket_id: str) -> bool:
        """Handle vehicle exit"""
        if ticket_id not in self.tickets:
            return False
        
        ticket = self.tickets[ticket_id]
        if not ticket.is_paid:
            return False
        
        vehicle_id = ticket.vehicle_id
        if vehicle_id not in self.vehicles:
            return False
        
        vehicle = self.vehicles[vehicle_id]
        spot_id = vehicle.parked_spot_id
        
        if spot_id not in self.spots:
            return False
        
        # Vacate the spot
        spot = self.spots[spot_id]
        result = spot.vacate()
        
        if result:
            # Update exit time
            ticket.complete_exit()
            vehicle.exit_time = ticket.exit_time
            return True
        
        return False

    def get_parking_status(self) -> Dict:
        """Get the current status of the parking lot"""
        total_spots = len(self.spots)
        occupied_spots = sum(1 for spot in self.spots.values() if spot.is_occupied)
        available_spots = total_spots - occupied_spots
        
        # Count by type
        type_counts = {}
        for spot_type in ParkingSpotType:
            total = sum(1 for spot in self.spots.values() if spot.spot_type == spot_type)
            occupied = sum(1 for spot in self.spots.values() if spot.spot_type == spot_type and spot.is_occupied)
            type_counts[spot_type.value] = {
                "total": total,
                "occupied": occupied,
                "available": total - occupied
            }
        
        # Count by level
        level_counts = {}
        for spot in self.spots.values():
            if spot.level not in level_counts:
                level_counts[spot.level] = {"total": 0, "occupied": 0}
            
            level_counts[spot.level]["total"] += 1
            if spot.is_occupied:
                level_counts[spot.level]["occupied"] += 1
        
        for level in level_counts:
            level_counts[level]["available"] = level_counts[level]["total"] - level_counts[level]["occupied"]
        
        # Record occupancy history
        current_time = datetime.datetime.now()
        occupancy_rate = (occupied_spots / total_spots) * 100 if total_spots > 0 else 0
        self.occupancy_history.append((current_time, occupancy_rate))
        
        return {
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "available_spots": available_spots,
            "occupancy_rate": occupancy_rate,
            "by_type": type_counts,
            "by_level": level_counts,
            "total_revenue": self.total_revenue
        }

    def predict_occupancy(self, hours_ahead: int = 1) -> float:
        """Predict the occupancy rate in the future based on historical data"""
        # Simple prediction based on average rate of change
        if len(self.occupancy_history) < 2:
            # Not enough data for prediction
            current_occupancy = self.get_parking_status()["occupancy_rate"]
            return current_occupancy
        
        # Calculate average rate of change per hour
        changes = []
        for i in range(1, len(self.occupancy_history)):
            prev_time, prev_rate = self.occupancy_history[i-1]
            curr_time, curr_rate = self.occupancy_history[i]
            
            time_diff = (curr_time - prev_time).total_seconds() / 3600  # hours
            if time_diff > 0:
                rate_change = (curr_rate - prev_rate) / time_diff
                changes.append(rate_change)
        
        if not changes:
            current_occupancy = self.get_parking_status()["occupancy_rate"]
            return current_occupancy
        
        avg_hourly_change = sum(changes) / len(changes)
        current_occupancy = self.get_parking_status()["occupancy_rate"]
        
        # Predict future occupancy
        predicted_occupancy = current_occupancy + (avg_hourly_change * hours_ahead)
        
        # Clamp between 0 and 100 percent
        return max(0, min(100, predicted_occupancy))

    def recommend_spot(self, vehicle_type: VehicleType, preference: str = "closest") -> Optional[str]:
        """Recommend a parking spot based on vehicle type and preference"""
        available_spots = []
        
        for spot_id, spot in self.spots.items():
            if not spot.is_occupied and self.is_spot_suitable(spot.spot_type, vehicle_type):
                available_spots.append(spot)
        
        if not available_spots:
            return None
        
        if preference == "closest":
            # Closest to entrance (assuming lower level and section A is closest)
            available_spots.sort(key=lambda spot: (spot.level, spot.section))
        elif preference == "level":
            # Specific level preference (assuming preference is a string like "level-2")
            try:
                preferred_level = int(preference.split("-")[1])
                # Filter spots on preferred level, or sort by closest level
                level_spots = [spot for spot in available_spots if spot.level == preferred_level]
                if level_spots:
                    available_spots = level_spots
            except:
                pass
        
        if available_spots:
            return available_spots[0].spot_id
        
        return None

    def is_spot_suitable(self, spot_type: ParkingSpotType, vehicle_type: VehicleType) -> bool:
        """Check if a spot type is suitable for a vehicle type"""
        if vehicle_type == VehicleType.CAR:
            return spot_type in [ParkingSpotType.REGULAR, ParkingSpotType.LARGE]
        elif vehicle_type == VehicleType.MOTORCYCLE:
            return spot_type in [ParkingSpotType.MOTORCYCLE, ParkingSpotType.REGULAR, ParkingSpotType.LARGE]
        elif vehicle_type == VehicleType.TRUCK:
            return spot_type == ParkingSpotType.LARGE
        elif vehicle_type == VehicleType.HANDICAPPED:
            return spot_type == ParkingSpotType.HANDICAPPED
        return False

    def get_busy_times(self) -> Dict[str, List[int]]:
        """Analyze historical data to determine busy times"""
        # In a real system, this would analyze actual data
        # Here we'll return a placeholder/simulated result
        
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        busy_times = {}
        
        for day in days_of_week:
            # Simulate busy hours based on typical patterns
            if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                busy_times[day] = [8, 9, 12, 13, 17, 18]  # Rush hours on weekdays
            else:
                busy_times[day] = [11, 12, 13, 14, 15, 16]  # Midday on weekends
        
        return busy_times

    def simulate_activity(self, hours: int = 24, interval_minutes: int = 15):
        """Simulate parking activity for a given period to generate data"""
        print(f"Starting parking activity simulation for {hours} hours...")
        
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=hours)
        current_time = start_time
        
        # Get vehicle types
        vehicle_types = list(VehicleType)
        
        # License plate generator
        def generate_license_plate():
            letters = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=3))
            numbers = ''.join(random.choices('0123456789', k=3))
            return f"{letters}-{numbers}"
        
        # Active ticket tracking
        active_tickets = []
        
        # Simulate activity at each interval
        while current_time < end_time:
            print(f"\nTime: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Determine entry probability based on time of day
            hour = current_time.hour
            day_of_week = current_time.strftime("%A")
            busy_times = self.get_busy_times()
            
            # Higher entry probability during busy hours
            is_busy_hour = hour in busy_times.get(day_of_week, [])
            entry_probability = 0.4 if is_busy_hour else 0.2
            
            # Process some exits
            for ticket_id in list(active_tickets):
                # Probability of exit increases with time parked
                ticket = self.tickets.get(ticket_id)
                if ticket and not ticket.exit_time:
                    vehicle = self.vehicles.get(ticket.vehicle_id)
                    if vehicle:
                        hours_parked = (current_time - ticket.entry_time).total_seconds() / 3600
                        exit_probability = min(0.3, hours_parked * 0.05)
                        
                        if random.random() < exit_probability:
                            # Pay ticket
                            self.pay_ticket(ticket_id)
                            # Exit vehicle
                            if self.vehicle_exit(ticket_id):
                                print(f"Vehicle with ticket {ticket_id} has exited")
                                active_tickets.remove(ticket_id)
            
            # Process some entries
            status = self.get_parking_status()
            if status["available_spots"] > 0 and random.random() < entry_probability:
                vehicle_type = random.choice(vehicle_types)
                license_plate = generate_license_plate()
                
                result = self.vehicle_entry(license_plate, vehicle_type)
                if result:
                    location, ticket_id = result
                    active_tickets.append(ticket_id)
                    print(f"Vehicle {license_plate} ({vehicle_type.value}) entered and parked at {location}")
            
            # Display current status
            status = self.get_parking_status()
            print(f"Occupancy: {status['occupied_spots']}/{status['total_spots']} spots ({status['occupancy_rate']:.1f}%)")
            print(f"Revenue: ${status['total_revenue']:.2f}")
            
            # Predict future occupancy
            prediction = self.predict_occupancy(hours_ahead=1)
            print(f"Predicted occupancy in 1 hour: {prediction:.1f}%")
            
            # Advance time
            current_time += datetime.timedelta(minutes=interval_minutes)
            time.sleep(0.1)  # Small delay for readability when running simulation
        
        print("\nSimulation completed.")

# Example usage
def demo():
    # Initialize parking system
    parking_ai = ParkingAI()
    parking_ai.initialize_parking_lot(levels=3, spots_per_level=40)
    
    # Show initial status
    status = parking_ai.get_parking_status()
    print(f"Parking initialized with {status['total_spots']} total spots")
    print(f"Available spots by type:")
    for spot_type, counts in status['by_type'].items():
        print(f"  {spot_type}: {counts['available']}/{counts['total']}")
    
    # Run a simulation
    parking_ai.simulate_activity(hours=3, interval_minutes=30)
    
    # Final status
    status = parking_ai.get_parking_status()
    print("\nFinal parking status:")
    print(f"Occupancy: {status['occupied_spots']}/{status['total_spots']} spots ({status['occupancy_rate']:.1f}%)")
    print(f"Total revenue: ${status['total_revenue']:.2f}")

if __name__ == "__main__":
    demo()
