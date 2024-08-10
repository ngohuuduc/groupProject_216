import json
import threading
import random
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import argparse
import time
import sys
import paho.mqtt.client as mqtt

from group_5_data_generator import SensorSimulator

class PublisherGUI(Tk):
    sensors_address = {
        "LivingRoom": "123.89.46.72",
        "Kitchen": "123.89.46.44",
        "Bath Room": "123.89.46.56",
        "Master Bedroom": "123.89.46.98",
        "Dining Room": "123.89.46.34",
        "Play Room": "123.89.46.65",
        "Laundry": "123.89.46.89"
    }

    def __init__(self, topic_name):
        super().__init__()
        self.title(f'Temperature Publisher - {topic_name}')
        self.__topic = topic_name

        # Initialize UI
        self.create_vars()
        self.create_ui()
        self.configureResizable()

        # Create Mqtt client
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id='pub_demo',
            protocol=mqtt.MQTTv5
        )
        # Register callbacks
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_publish = self.on_publish

    def configureResizable(self):
        max_row = 12
        max_col = 2
        for row_index in range(max_row):
            Grid.rowconfigure(self, index=row_index, weight=1)
        Grid.columnconfigure(self, index=0, weight=1)
        Grid.columnconfigure(self, index=1, weight=3)

    def create_vars(self):
        self.__flag_status = False
        self.__name = StringVar()
        self.__time = StringVar()
        self.__base = StringVar()
        self.__min = StringVar()
        self.__max = StringVar()
        self.__delta = StringVar()
        self.__min_step = StringVar()
        self.__max_step = StringVar()
        self.__min_cycle = StringVar()
        self.__max_cycle = StringVar()
        self.__squiggle = BooleanVar()
        self.__button_name = StringVar(value='Start')
        self.__status = StringVar(value='Standby')

        # dropdown options
        self.__minMaxValues = [18, 18.5, 19, 19.5, 20, 20.5, 21]
        self.__stepsValues = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        self.__cycleValues = [1, 2, 3, 4]
        self.__sensors_name = list(self.sensors_address.keys())
        self.__time_intervals = [0.25, 0.5, 1, 1.5, 2, 2.5]
        self.__max_iteration = 100

    def create_ui(self, parent=None):
        if not parent:
            parent = self

        Label(
            parent,
            text='Publisher Parameters',
            font=('Arial Bold', 14),
            anchor='c',
            justify='center',
        ).grid(row=0, columnspan=2, sticky='nsew', pady=(20, 10))

        Label(parent, text='Sensor Name:', font=('Arial', 10), anchor='w').grid(row=1, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Time Interval (seconds):', font=('Arial', 10), anchor='w').grid(row=2, column=0, sticky='nsew', pady=(0, 5), padx=(3, 0))
        Label(parent, text='Starting Temp:', font=('Arial' ,10), anchor='w').grid(row=3, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Minimum Temp:', font=('Arial' ,10), anchor='w').grid(row=4, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Max Temp:', font=('Arial' ,10), anchor='w').grid(row=5, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Delta (Range: -1-1):', font=('Arial' ,10), anchor='w').grid(row=6, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Min Step:', font=('Arial' ,10), anchor='w').grid(row=7, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Max Step:', font=('Arial' ,10), anchor='w').grid(row=8, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Min Cycle:', font=('Arial' ,10), anchor='w').grid(row=9, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Max Cycle:', font=('Arial' ,10), anchor='w').grid(row=10, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))
        Label(parent, text='Squiggle:', font=('Arial' ,10), anchor='w').grid(row=11, column=0, sticky='nsew', pady=(0, 5), padx=(3,0))

        # Create dropdowns and other widgets
        nameComboBox = Combobox(parent, width=20, textvariable=self.__name)
        nameComboBox['values'] = self.__sensors_name
        nameComboBox.current(5)
        nameComboBox.grid(row=1, column=1, sticky='W', pady=(0, 1))

        timeComboBox = Combobox(parent, width=20, textvariable=self.__time)
        timeComboBox['values'] = self.__time_intervals
        timeComboBox.current(0)
        timeComboBox.grid(row=2, column=1, sticky='W', pady=(0, 1))

        minComboBox = Combobox(parent, width=20, textvariable=self.__base)
        minComboBox['values'] = self.__minMaxValues
        minComboBox.current(1)
        minComboBox.grid(row=3, column=1, sticky='W', pady=(0, 5))

        minComboBox = Combobox(parent, width=20, textvariable=self.__min)
        minComboBox['values'] = self.__minMaxValues
        minComboBox.current(0)
        minComboBox.grid(row=4, column=1, sticky='W', pady=(0, 5))

        maxComboBox = Combobox(parent, width=20, textvariable=self.__max)
        maxComboBox['values'] = self.__minMaxValues
        maxComboBox.current(6)
        maxComboBox.grid(row=5, column=1, sticky='W', pady=(0, 5))

        e = Entry(
            parent,
            textvariable=self.__delta,
            width=23
        )
        e.insert(0, '1')
        e.grid(row=6, column=1, sticky=W, pady=(0, 5))

        minStepComboBox = Combobox(parent, width=20, textvariable=self.__min_step)
        minStepComboBox['values'] = self.__stepsValues
        minStepComboBox.current(0)
        minStepComboBox.grid(row=7, column=1, sticky='W', pady=(0, 5))

        maxStepComboBox = Combobox(parent, width=20, textvariable=self.__max_step)
        maxStepComboBox['values'] = self.__stepsValues
        maxStepComboBox.current(6)
        maxStepComboBox.grid(row=8, column=1, sticky='W', pady=(0, 5))

        minCycleComboBox = Combobox(parent, width=20, textvariable=self.__min_cycle)
        minCycleComboBox['values'] = self.__cycleValues
        minCycleComboBox.current(0)
        minCycleComboBox.grid(row=9, column=1, sticky='W', pady=(0, 5))

        maxCycleComboBox = Combobox(parent, width=20, textvariable=self.__max_cycle)
        maxCycleComboBox['values'] = self.__cycleValues
        maxCycleComboBox.current(3)
        maxCycleComboBox.grid(row=10, column=1, sticky='W', pady=(0, 5))

        check = Checkbutton(parent, text="Squiggle", variable=self.__squiggle)
        check.grid(row=11, column=1, sticky='W', pady=(0, 5))

        Button(parent, textvariable=self.__button_name, command=self.btn_click).grid(row=12, columnspan=2, pady=(10, 20))

        Label(parent, textvariable=self.__status, font=('Arial', 10), anchor='w').grid(row=13, columnspan=2, sticky='nsew')

    def btn_click(self):
        if self.__button_name.get() == 'Start':
            self.__button_name.set('Stop')
            self.__flag_status = True
            # parse values to float for validation
            try:
                parsedBase = float(self.__base.get())
                parsedMin = float(self.__min.get())
                parsedMax = float(self.__max.get())
                parsedMinStep = float(self.__min_step.get())
                parsedMaxStep = float(self.__max_step.get())
                parsedMinCycle = int(self.__min_cycle.get())
                parsedMaxCycle = int(self.__max_cycle.get())
                parsedName = self.__name.get()
                parsedInterval = float(self.__time.get())

                # Validate delta value
                parsedDelta = float(self.__delta.get())
                if(parsedDelta < -1 or parsedDelta > 1):
                    messagebox.showinfo(title='Information', message="Delta must be from -1 to 1")
                    return

                if (parsedMaxCycle <= parsedMinCycle):
                    messagebox.showinfo(title='Information', message="Max cycle must be greater than min cycle")
                    return

                self.mqttc.connect(host='localhost', port=1883)
                thread = threading.Thread(
                    target=self.run,
                    args=[parsedBase, parsedMin, parsedMax, parsedDelta, parsedMinStep, parsedMaxStep, parsedMinCycle, parsedMaxCycle, parsedName, parsedInterval])
                thread.daemon = True
                thread.start()

            except ValueError as e:
                messagebox.showinfo(title='Information', message=f'Error parsing input: {e}')
            except Exception as e:
                messagebox.showinfo(title='Information', message=f'Unexpected error: {e}')
                
        else:
            self.__button_name.set('Start')
            self.__status.set('Standby')
            self.__flag_status = False

    def run(self, parsedBase, parsedMin, parsedMax, parsedDelta, parsedMinStep, parsedMaxStep, parsedMinCycle, parsedMaxCycle, parsedName, parsedInterval):
        tempGenerator = SensorSimulator(
            min_value=parsedMin, max_value=parsedMax, delta=parsedDelta,
            base_value=parsedBase, min_step=parsedMinStep, max_step=parsedMaxStep,
            min_cycle=parsedMinCycle, max_cycle=parsedMaxCycle,
            squiggle=self.__squiggle.get()
        )
        miss_transmission = random.randint(1, self.__max_iteration)
        wild_transmission = random.randint(1, self.__max_iteration)
        iteration = 0
        while self.__flag_status:
            iteration += 1
            if iteration > self.__max_iteration:
                iteration = 0
                miss_transmission = random.randint(1, self.__max_iteration)
                wild_transmission = random.randint(1, self.__max_iteration)

            if miss_transmission == iteration:
                time.sleep(parsedInterval)
                continue

            temp = tempGenerator.value
            if wild_transmission == iteration:
                temp = temp * random.randint(2,10)

            try:
                packetId = int(time.time() * 1000)
                msg_dict = {
                    "packetId": packetId,
                    "name": parsedName,
                    "ipv4": self.sensors_address[parsedName],
                    "temp": temp,
                    "interval": parsedInterval
                }
                data = json.dumps(msg_dict, indent=4, sort_keys=True, default=str)
                self.mqttc.publish(topic=self.__topic, payload=data, qos=0)
                self.__status.set(f'Packet Sending: {msg_dict["packetId"]}')
                time.sleep(parsedInterval)

            except (KeyboardInterrupt, SystemExit):
                self.mqttc.disconnect()
                sys.exit()

    def on_connect(self, mqttc, userdata, flags, rc):
        print('Connected.. \n Return code: ' + str(rc))

    def on_disconnect(self, mqttc, userdata, rc):
        print('disconnected..')

    def on_message(self, mqttc, userdata, msg):
        print('"\n------ Received Message ------\n"')
        print('Topic: ' + msg.topic + ', Message: ' + str(msg.payload))

    def on_publish(self, client, userdata, mid, reason, properties):
        print(f'Publish message {mid} -- code {reason}')

    def publish(self, topic, payload, qos=0):
        self.mqttc.publish(topic=topic, payload=payload, qos=qos)
        return

    def disconnect(self):
        self.mqttc.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="Topic name", required=True, type=str)
    args = parser.parse_args()
    rmPub = PublisherGUI(topic_name=args.topic)
    rmPub.geometry("400x300")
    rmPub.minsize(width=450, height=400)
    rmPub.mainloop()


