import random
import matplotlib.pyplot as plt

class SensorSimulator:
    def __init__(self, min_value=18.0, max_value=21.0, noise_level=0.2, base_value=18.5, min_step=0, max_step=0.6, delta=0.08, min_cycle=1, max_cycle=4, squiggle=False):
        self.min_value = min_value
        self.max_value = max_value
        self.noise_level = noise_level
        self.base_value = base_value
        self.min_step = min_step if delta > 0 else -min_step
        self.max_step = max_step if delta > 0 else -max_step
        self.delta = delta
        self.min_cycle = min_cycle
        self.max_cycle = max_cycle
        self.cycle = random.randint(self.min_cycle, self.max_cycle)
        self.half_cycle = self.cycle / 2
        self.squiggle = squiggle == 'True'
        random.seed("COMP216Group3")

    def _generate_normalized_value(self):
        """Generate a normalized value with randomness and noise."""
        value = random.random()
        return value

    @property
    def value(self):
        """Generate the sensor value based on the temperature algorithm."""
        normalized_value = self._generate_normalized_value()

        # Decrease Cycle every new Temp
        self.cycle -= 1
        if self.cycle < 0:
            self._reset_cycle()

        # Calculate the next value
        increment = (normalized_value * self.delta * 5) + self.min_step
        increment = self.max_step if (abs(increment) > abs(self.max_step)) else increment
        if self.squiggle and self.cycle == self.half_cycle: 
            increment *= -1
        self.base_value += increment

        # Clip to max and min values
        if self.base_value > self.max_value:
            self.base_value = self.max_value
            self._reset_cycle()
        if self.base_value < self.min_value:
            self.base_value = self.min_value
            self._reset_cycle()

        return self.base_value

    def _reset_cycle(self):
        """Reset cycle and adjust parameters for next value generation."""
        self.cycle = random.randint(self.min_cycle, self.max_cycle)
        self.half_cycle = self.cycle / 2
        self.delta *= -1
        self.min_step *= -1
        self.max_step *= -1

    def generate_data(self, num_points=200):
        return [self.value for _ in range(num_points)]

# Example usage
if __name__ == "__main__":
    sensor = SensorSimulator(base_value=18.5, min_value=18.0, max_value=21.0, min_step=0, max_step=0.6, delta=0.08, min_cycle=1, max_cycle=4, squiggle='False')
    data = sensor.generate_data(num_points=500)

    # Plotting the data
    plt.plot(data)
    plt.title('Simulated Sensor Data')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()
