import random
import matplotlib.pyplot as plt

class SensorSimulator:
    def __init__(self, min_value=18.0, max_value=21.0, noise_level=0.2, base_value=18.5, 
                 min_step=0, max_step=0.6, delta=0.08, min_cycle=1, max_cycle=4, 
                 squiggle=False, seed=None):
        """
        Initialize the SensorSimulator with customizable parameters for data generation.

        Parameters:
        min_value (float): Minimum possible value.
        max_value (float): Maximum possible value.
        noise_level (float): Amount of noise to introduce in the data.
        base_value (float): Starting value for the sensor.
        min_step (float): Minimum step size for value changes.
        max_step (float): Maximum step size for value changes.
        delta (float): Direction and magnitude influence on step changes.
        min_cycle (int): Minimum cycle length before resetting.
        max_cycle (int): Maximum cycle length before resetting.
        squiggle (bool): If True, introduces squiggles in the data.
        seed (int): Random seed for reproducibility.
        """
        self.min_value = min_value
        self.max_value = max_value
        self.noise_level = noise_level
        self.base_value = base_value
        self.min_step = min_step
        self.max_step = max_step
        self.delta = delta
        self.min_cycle = min_cycle
        self.max_cycle = max_cycle
        self.cycle = random.randint(self.min_cycle, self.max_cycle)
        self.half_cycle = self.cycle / 2
        self.squiggle = squiggle
        
        if seed is not None:
            random.seed(seed)

    def _generate_normalized_value(self):
        """Generate a normalized value with randomness and noise."""
        return random.random()

    def _apply_noise(self, value):
        """Apply noise to the generated value."""
        return value + (random.uniform(-1, 1) * self.noise_level)

    def _clip_value(self, value):
        """Ensure the value stays within the defined range."""
        return max(self.min_value, min(value, self.max_value))

    def _adjust_increment(self, normalized_value):
        """Calculate the increment based on the normalized value."""
        increment = (normalized_value * self.delta * 5) + self.min_step
        return min(max(increment, self.min_step), self.max_step)

    def _reset_cycle(self):
        """Reset cycle and adjust parameters for next value generation."""
        self.cycle = random.randint(self.min_cycle, self.max_cycle)
        self.half_cycle = self.cycle / 2
        self.delta *= -1
        self.min_step *= -1
        self.max_step *= -1

    @property
    def value(self):
        """Generate the sensor value based on the algorithm."""
        normalized_value = self._generate_normalized_value()
        self.cycle -= 1
        if self.cycle < 0:
            self._reset_cycle()

        increment = self._adjust_increment(normalized_value)
        if self.squiggle and self.cycle == self.half_cycle:
            increment *= -1
        self.base_value += increment
        self.base_value = self._clip_value(self.base_value)
        self.base_value = self._apply_noise(self.base_value)

        return self.base_value

    def generate_data(self, num_points=200):
        """Generate a list of sensor values."""
        return [self.value for _ in range(num_points)]

    def plot_data(self, data):
        """Plot the generated sensor data."""
        plt.plot(data)
        plt.title('Simulated Sensor Data')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    sensor = SensorSimulator(seed=42)
    data = sensor.generate_data(num_points=500)
    sensor.plot_data(data)

