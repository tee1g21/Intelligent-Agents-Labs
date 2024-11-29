from mable.cargo_bidding import TradingCompany
from mable.examples import environment, fleets, shipping, companies


class MyCompany(TradingCompany):

    def pre_inform(self, trades, time):        
        self._future_trades = trades
        print(f"\nPre-informed of {len(self._future_trades)} future trades:")
        for trade in self._future_trades:
            print(trade.origin_port.name, "-> ", trade.destination_port.name)
        print()

    def inform(self, trades, *args, **kwargs):
        print(f"\nInformed of {len(trades)} trades.")

        return []

    def receive(self, contracts, auction_ledger=None, *args, **kwargs):
        #print(f"Received {len(contracts)} contracts.\n")
        competitor_name = "Arch Enemy Ltd."
        competitor_won_contracts = auction_ledger[competitor_name]
        competitor_fleet = [c for c in self.headquarters.get_companies() if c.name == competitor_name].pop().fleet
        
        if competitor_won_contracts:
            for contract in competitor_won_contracts:
                trade = contract.trade
                competitor_bid = contract.payment

            competitor_vessel = competitor_fleet[0]  # Pick the first vessel
            predicted_cost = self.predict_cost(competitor_vessel, trade)
            
            if predicted_cost > 0:
                bid_factor = competitor_bid / predicted_cost
            else:
                bid_factor = float('inf')
                
            print(f"Trade: {trade.origin_port.name} -> {trade.destination_port.name}")
            print(f" Competitor Bid: {competitor_bid}")
            print(f" Predicted Cost: {predicted_cost}")
            print(f" Bid Factor: {bid_factor}")

    
            
    def predict_cost(self, vessel, trade):
        
        loading_time = vessel.get_loading_time(trade.cargo_type, trade.amount)
        loading_costs = vessel.get_loading_consumption(loading_time)
        unloading_costs = vessel.get_unloading_consumption(loading_time)
        travel_distance = self.headquarters.get_network_distance(
            trade.origin_port, trade.destination_port)
        travel_time = vessel.get_travel_time(travel_distance)
        travel_cost = vessel.get_laden_consumption(travel_time, vessel.speed)
        total_cost = loading_costs + unloading_costs + travel_cost  
        
        return total_cost


def build_specification():
    specifications_builder = environment.get_specification_builder(fixed_trades=shipping.example_trades_1())
    fleet = fleets.example_fleet_1()
    specifications_builder.add_company(MyCompany.Data(MyCompany, fleet, MyCompany.__name__))
    specifications_builder.add_company(
        companies.MyArchEnemy.Data(companies.MyArchEnemy, fleets.example_fleet_2(), "Arch Enemy Ltd."))
    sim = environment.generate_simulation(
        specifications_builder,
        show_detailed_auction_outcome=True)
    sim.run()


if __name__ == '__main__':
    build_specification()
