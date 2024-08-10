from tkinter import *
from tkinter import Tk, Canvas, Frame, W
from tkinter import messagebox
from tkinter.ttk import *
import paho.mqtt.client as mqtt
import json

class TempClient(Tk):
    def __init__(self):
        super().__init__()
        self.title('Group5 - Sensor Client')
        self.create_vars()

        # Initialize UI
        self.initUI()

        # Initialize MQTT connection
        mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id='sub_demo',
            protocol=mqtt.MQTTv5
        )
        mqttc.on_connect = self.on_connect
        mqttc.on_disconnect = self.on_disconnect
        mqttc.on_message = self.on_message
        mqttc.on_subscribe = self.on_subscribe
        mqttc.on_unsubscribe = self.on_unsubscribed
        self.__mqttc = mqttc

    def on_disconnect(self, mqttc, userdata, rc, properties=None):
        print('Disconnected.. \n Return code: ' + str(rc))


    def on_unsubscribed(self, mqttc, userdata, mid, granted_qos):
        print('Unsubscribed')

    def update_data(self, packetId, interval, newTemp):
        # Check if there is lost transmission
        lost = (packetId - self.__lastReceived) > (interval * 1000 * 1.1)
        if (self.__lastReceived > 0 and lost):
            print('Missing Detected!')
            miss = self.__missing.get()
            self.__missing.set(miss + 1)

        self.__lastReceived = packetId

        # Wild Data is not added to dataset
        if (newTemp < -40 or newTemp > 40):
            print('Wild Detected!')
            wild = self.__wild.get()
            self.__wild.set(wild + 1)
            return
        
        if(len(self.__data) >= 20):
            self.__data.pop(0)

        self.__data.append(newTemp)

        # Method to Display Rectangles and Lines
        self.canv.delete('all')
        self.displayLines()
        self.displayData()

    def create_styles(self, parent=None):
        style = Style()
        style.configure('TFrame', background='#c8e6d3')
        style.configure('TLabel', background='#c8e6d3')

    def create_vars(self):
        self.__data = []
        self.__sensorName = StringVar()
        self.__packetId = StringVar(value='000000000000')
        self.__name = StringVar(value='Sensor Name')
        self.__temp = DoubleVar(value=0)
        self.__ipv4 = StringVar(value='0.0.0.0')
        self.__wild = IntVar(value=0)
        self.__missing = IntVar(value=0)
        self.__lastReceived = -1
        self.__button_name = StringVar(value='Start')

        # dropdown options
        self.__sensors_name = ["sensor1", "sensor2", "sensor3"]

    def initUI(self):
        Canvas(width=860, height=280).pack()
        container = Frame(self, padding=(5, 5))
        container.place(relx=0.015, rely=0.02, relheight=0.96, relwidth=0.97)
        Label(container, text='Temperature Client', font='Arial 12 bold').place(relx=0.33, height=30)
        Label(container, text='PacketID: ').place(relx=0.7, rely=0.15)
        Label(container, textvariable=self.__packetId).place(relx=0.85, rely=0.15)
        Label(container, text='Name: ').place(relx=0.7, rely=0.25)
        Label(container, textvariable=self.__name).place(relx=0.85, rely=0.25)
        Label(container, text='IPv4: ').place(relx=0.7, rely=0.35)
        Label(container, textvariable=self.__ipv4).place(relx=0.85, rely=0.35)
        Label(container, text='Temperature: ').place(relx=0.7, rely=0.45)
        Label(container, textvariable=self.__temp).place(relx=0.85, rely=0.45)
        Label(container, text='Wild Data: ').place(relx=0.7, rely=0.55)
        Label(container, textvariable=self.__wild).place(relx=0.85, rely=0.55)
        Label(container, text='Missing: ').place(relx=0.7, rely=0.65)
        Label(container, textvariable=self.__missing).place(relx=0.85, rely=0.65)
        topicOptions = Combobox(container, values=self.__sensors_name, textvariable=self.__sensorName, width=10)
        topicOptions.place(relx=0.7, rely=0.85)
        topicOptions.current(0)
        self.startButton = Button(textvariable=self.__button_name, command=self.btn_on_click).place(relx=0.83, rely=0.82)
        # Initialize Canvas
        self.canv = Canvas(self)
        self.canv.place(relx=0.05, rely=0.24, width=500, height=180)

        # Initialize Start Value
        self.create_styles()

    def btn_on_click(self):
        if self.__button_name.get() == 'Start':
            # Set States
            self.__button_name.set('Stop')
            self.__data.clear()
            self.__lastReceived = -1
            self.__wild.set(0)
            self.__missing.set(0)
            # Connect to Mqtt broker on specified host and port
            self.__mqttc.connect(host='localhost', port=1883)
            self.__mqttc.loop_start()
            print('Starting:', self.__sensorName.get())
        else:
            self.__button_name.set('Start')
            self.__mqttc.unsubscribe(topic=self.__sensorName.get())
            self.__mqttc.loop_stop()

    def on_connect(self, mqttc, userdata, flags, rc, properties=None):
        print('Connected.. \n Return code: ' + str(rc))
        mqttc.subscribe(topic=self.__sensorName.get(), qos=0)


    def on_message(self, mqttc, userdata, msg):
        message = json.loads(msg.payload)
        self.__packetId.set(message['packetId'])
        self.__name.set(message['name'])
        self.__temp.set(message['temp'])
        self.__ipv4.set(message['ipv4'])
        self.update_data(message['packetId'], message['interval'], message['temp'])

    def on_subscribe(self, mqttc, userdata, mid, granted_qos, properties=None):
        print('Subscribed')

    
    def displayLines(self):
        self.canv = Canvas(self)
        self.canv.place(relx=0.1, rely=0.24, width=500, height=180)

        lineHeight = 10
        textDisplay = 22
        for _ in range(4):
            self.canv.create_text(25, lineHeight, anchor=W, font='Arial 7', text=textDisplay)
            self.canv.create_line(45, lineHeight, 65, lineHeight)
            self.canv.create_line(50, lineHeight+20, 65, lineHeight+20)
            lineHeight += 40
            textDisplay -= 1

        self.canv.create_text(25, lineHeight, anchor=W, font='Arial 7', text=textDisplay)
        self.canv.create_line(45, lineHeight, 65, lineHeight)

    def displayData(self):
        spacing = 70
        prevY = 0
        data_count = len(self.__data)
        for i in range(data_count):
            full = 170 - 10
            relative = (self.__data[i] - 18) / (22 - 18)
            height = 170 - (relative * full)
            
            # Line - No line if data is less than 2 counts
            if(i > 0):
                self.canv.create_line(spacing, prevY, spacing + 20, height)
            
            spacing += 20
            prevY = height

if __name__ == '__main__':
    sts = TempClient()
    sts.mainloop()
