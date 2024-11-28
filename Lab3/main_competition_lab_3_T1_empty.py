from mable.cargo_bidding import TradingCompany
from mable.examples import environment, fleets, shipping
from mable.transport_operation import Bid, ScheduleProposal


class MyCompany(TradingCompany):

    def __init__(self, fleet, name):
        super().__init__(fleet, name)
        self._future_trades = None

    def pre_inform(self, trades, time):        
        self._future_trades = trades
        print(f"\nPre-informed of {len(self._future_trades)} future trades:")
        for trade in self._future_trades:
            print(trade.origin_port.name, "-> ", trade.destination_port.name)
        print()

    def inform(self, trades, *args, **kwargs):
        print(f"\nInformed of {len(trades)} trades.")
        proposed_scheduling = self.propose_schedules(trades)
        scheduled_trades = proposed_scheduling.scheduled_trades
        self._current_scheduling_proposal = proposed_scheduling
        trades_and_costs = [
            (x, proposed_scheduling.costs[x]) if x in proposed_scheduling.costs
            else (x, 0)
            for x in scheduled_trades]
        bids = [Bid(amount=cost, trade=one_trade) for one_trade, cost in trades_and_costs]
        self._future_trades = None
        return bids

    def receive(self, contracts, auction_ledger=None, *args, **kwargs):
        print(f"Received {len(contracts)} contracts.\n")
        trades = [one_contract.trade for one_contract in contracts]
        scheduling_proposal = self.find_schedules(trades)
        rejected_trades = self.apply_schedules(scheduling_proposal.schedules)

    def propose_schedules(self, trades):
        schedules = {}
        costs = {}
        scheduled_trades = []
        
        j = 0
        while j < len(self._fleet):
            current_vessel = self.fleet[j] # print current vessel location 
            print(f"Current vessel location: {current_vessel.location.name}") 
            
            current_vessel_schedule = schedules.get(current_vessel, current_vessel.schedule)
            new_schedule = current_vessel_schedule.copy()
            i = 0
            trade_options = {}
            while i < len(trades):
                current_trade = trades[i]
                new_schedule.add_transportation(current_trade)
                if new_schedule.verify_schedule():
                    
                    # calculate cost based on predict cost logic
                    total_cost = self.predict_cost(current_vessel, current_trade)
                    print(f"Trade {i+1} cost: {total_cost}. {current_trade.origin_port.name} -> {current_trade.destination_port.name}")
                    
                    #trade options currently based on cost
                    trade_options[current_trade] = total_cost
                 
            
                else: 
                    print(f"Schedule not valid for trade: {current_trade.origin_port.name} -> {current_trade.destination_port.name} ")
                     
                i += 1
            if len(trade_options) > 0:
                
                schedules[current_vessel] = new_schedule
                
                # select trade with lowest distance
                selected_trade = min(trade_options, key=trade_options.get)
                print(f"Selected trade: {selected_trade.origin_port.name} -> {selected_trade.destination_port.name}")
                scheduled_trades.append(selected_trade)
                
                # add cost to costs dictionary
                costs[selected_trade] = trade_options[selected_trade]
                
            j += 1
        return ScheduleProposal(schedules, scheduled_trades, costs)


        
    def predict_cost(self, vessel, trade):
        
        #vessel speed
        speed = vessel.speed
        
        # cost of laden travel
        laden_distance = self.headquarters.get_network_distance(vessel.location, trade.origin_port)
        laden_travel_time = vessel.get_travel_time(laden_distance)
        laden_cost = vessel.get_laden_consumption(laden_travel_time, speed)
        
        # cost of ballast travel
        ballast_distance = self.headquarters.get_network_distance(trade.origin_port, trade.destination_port)
        ballast_travel_time = vessel.get_travel_time(ballast_distance)
        ballast_cost = vessel.get_ballast_consumption(ballast_travel_time, speed)
        
        # loading/unloading costs
        loading_fuel_cost = vessel.get_loading_consumption(trade.amount)
        unloading_fuel_cost = vessel.get_unloading_consumption(trade.amount)

        # sum costs
        total_cost = laden_cost + ballast_cost + loading_fuel_cost + unloading_fuel_cost
        
        return total_cost

    def find_schedules(self, trades):
        schedules = {}
        scheduled_trades = []
        i = 0
        while i < len(trades):
            current_trade = trades[i]
            is_assigned = False
            j = 0
            while j < len(self._fleet) and not is_assigned:
                current_vessel = self._fleet[j]
                current_vessel_schedule = schedules.get(current_vessel, current_vessel.schedule)
                new_schedule = current_vessel_schedule.copy()
                new_schedule.add_transportation(current_trade)
                if new_schedule.verify_schedule():
                    schedules[current_vessel] = new_schedule
                    scheduled_trades.append(current_trade)
                    is_assigned = True
                j += 1
            i += 1
        return ScheduleProposal(schedules, scheduled_trades, {})


def build_specification():
    specifications_builder = environment.get_specification_builder(fixed_trades=shipping.example_trades_1())
    fleet = fleets.example_fleet_1()
    specifications_builder.add_company(MyCompany.Data(MyCompany, fleet, MyCompany.__name__))
    sim = environment.generate_simulation(
        specifications_builder,
        show_detailed_auction_outcome=True)
    sim.run()


if __name__ == '__main__':
    build_specification()


   #if self._future_trades is not None:
                    #    for future_trade in self._future_trades:
                    #        distance = self.headquarters.get_network_distance(
                    #            current_trade.destination_port, future_trade.origin_port
                    #        )
                    #        print(f"Trade Distance: {distance}. {current_trade.destination_port.name} -> {future_trade.origin_port.name}")
                    #else:
                    #    print("No future trades")