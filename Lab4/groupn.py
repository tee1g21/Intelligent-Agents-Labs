from mable.cargo_bidding import TradingCompany
from mable.transport_operation import ScheduleProposal

class groupn(TradingCompany):
    
    def __init__(self, fleet, name, profit_factor=1.65):
        super().__init__(fleet, name, profit_factor)
        
    def pre_inform(self, trades, time):
        return super().pre_inform(trades, time)
    
    def inform(self, trades, *args, **kwargs):
        return super().inform(trades, *args, **kwargs)
    
    def receive(self, contracts, auction_ledger=None, *args, **kwargs):
        return super().receive(contracts, auction_ledger, *args, **kwargs)
    
    def propose_schedules(self, trades):
        schedules = {}
        scheduled_trades = []
        costs = {}
        
        return ScheduleProposal(schedules, scheduled_trades, costs)
    
    def predict_cost(self, vessel, trade):
        
        # calculate loading and unloading costs
        loading_time = vessel.get_loading_time(trade.cargo_type, trade.amount)
        loading_costs = vessel.get_loading_consumption(loading_time)
        unloading_costs = vessel.get_unloading_consumption(loading_time)
        
        # calculate travel costs
        travel_distance = self.headquarters.get_network_distance(
            trade.origin_port, trade.destination_port)
        travel_time = vessel.get_travel_time(travel_distance)
        travel_cost = vessel.get_laden_consumption(travel_time, vessel.speed)
        
        # calculate total cost
        total_cost = loading_costs + unloading_costs + travel_cost  
        
        return total_cost
    
    def find_competing_vessels(self, trade):
        competing_vessels = {}                
        companies = self.headquarters.get_companies()

        # Find the closest vessel for each company
        if companies:
            for company in companies:
                closest_vessel = None
                min_distance = float('inf')

                for vessel in company.fleet:                    
                    print(f"{company.name}'s {vessel.name}")                    
                    # distance from vessel to trade origin port
                    distance = self.headquarters.get_network_distance(vessel.location, trade.origin_port)
                    # update min distance and closest vessel
                    if distance < min_distance:
                        min_distance = distance
                        closest_vessel = vessel

                # add the closest vessel to competing vessels
                if closest_vessel:
                    competing_vessels[company] = closest_vessel
                    
        return competing_vessels