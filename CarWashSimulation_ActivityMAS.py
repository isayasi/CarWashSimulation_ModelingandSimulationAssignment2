import simpy
import random
import matplotlib.pyplot as plt

# Simulation Parameters
RANDOM_SEED = 42
NUM_WASH_BAYS = 2  # Number of washing stations
MAX_QUEUE_SIZE = 5  # Maximum cars allowed in queue
SIMULATION_DURATION = 50
CAR_ARRIVAL_RATE = 2  # Average car arrival rate (cars per time unit)
WASH_DURATION = (3, 5)  # Random time for washing a car (min, max)

class CarWashSimulation:
    def __init__(self, environment, wash_bays_count):
        self.env = environment
        self.wash_bays = simpy.Resource(environment, wash_bays_count)
        self.cars_washed_count = 0
        self.queue_sizes = []
        self.waiting_times_list = []
        self.total_wait_time = 0

    def car_arrival_process(self):
        while True:
            # Time until the next car arrives
            interarrival_time = random.expovariate(1.0 / CAR_ARRIVAL_RATE)
            yield self.env.timeout(interarrival_time)

            # Check the queue size
            if len(self.wash_bays.queue) < MAX_QUEUE_SIZE:
                self.env.process(self.wash_car_process())
            else:
                # If the queue is full, the car leaves (simulating a drop)
                print("A car left due to a full queue.")

            # Record the current queue size
            self.queue_sizes.append(len(self.wash_bays.queue))

    def wash_car_process(self):
        arrival_time = self.env.now  # Record the arrival time of the car
        with self.wash_bays.request() as request:
            yield request  # Wait for a wash bay to become available
            wash_time = random.uniform(*WASH_DURATION)
            yield self.env.timeout(wash_time)  # Wash the car

            # Update statistics
            self.cars_washed_count += 1
            wait_time = self.env.now - arrival_time  # Calculate waiting time
            self.waiting_times_list.append(wait_time)
            self.total_wait_time += wait_time

def run_car_wash_simulation():
    random.seed(RANDOM_SEED)
    simulation_env = simpy.Environment()
    car_wash = CarWashSimulation(simulation_env, NUM_WASH_BAYS)

    # Start car arrival process
    simulation_env.process(car_wash.car_arrival_process())

    # Run the simulation
    simulation_env.run(until=SIMULATION_DURATION)

    return car_wash.cars_washed_count, car_wash.queue_sizes, car_wash.total_wait_time

def plot_results(queue_lengths):
    plt.figure(figsize=(12, 6))

    # Plot queue length over time
    plt.plot(queue_lengths, label='Queue Length', color='blue')
    plt.xlabel('Time')
    plt.ylabel('Current Queue Length')
    plt.title('Current Queue Length Over Time')
    plt.axhline(y=MAX_QUEUE_SIZE, color='red', linestyle='--', label='Max Queue Size')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    total_runs = 50
    total_cars_washed_all_runs = []
    total_wait_times_all_runs = []

    for _ in range(total_runs):
        total_cars_washed, queue_sizes, total_wait_time = run_car_wash_simulation()
        total_cars_washed_all_runs.append(total_cars_washed)
        total_wait_times_all_runs.append(total_wait_time)

    # Analyze results
    average_cars_washed = sum(total_cars_washed_all_runs) / total_runs
    average_wait_time = sum(total_wait_times_all_runs) / total_runs

    print(f'Average Total Cars Washed over {total_runs} runs: {average_cars_washed}')
    print(f'Average Total Waiting Time over {total_runs} runs: {average_wait_time:.2f} time units')

    # Run simulation and plot the results
    total_cars_washed, queue_lengths, total_waiting_time = run_car_wash_simulation()
    print(f'Total Cars Washed: {total_cars_washed}')
    print(f'Total Waiting Time: {total_waiting_time:.2f} time units')
    plot_results(queue_lengths)
