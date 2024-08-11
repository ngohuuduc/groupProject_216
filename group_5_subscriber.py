from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import paho.mqtt.client as mqtt
import json
import smtplib
from email.mime.text import MIMEText
from random import randint
import time
import os
from dotenv import load_dotenv
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),  # Logs to console
                        logging.FileHandler("Subscriber.log")  # Logs to file
                        
                    ])
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

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

    def send_email_notification(self, subject, message):
        try:
            sender_email = os.getenv('SENDER_EMAIL')
            receiver_email = os.getenv('RECEIVER_EMAIL')
            password = os.getenv('EMAIL_PASSWORD')
            
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = receiver_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, password)
                server.send_message(msg)
            logging.info(f"Email sent: {subject}")
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred: {e}")
            messagebox.showerror("Email Error", "Failed to send email notification.")

    def on_disconnect(self, client, userdata, flags, reason, properties):
        logging.info('Disconnected.. \n Return code: ' + str(reason))

    def on_unsubscribed(self, mqttc, userdata, mid, granted_qos):
        logging.info('Unsubscribed')

    def update_data(self, packetId, interval, newTemp):
        # Check if there is lost transmission
        lost = (packetId - self.__lastReceived) > (interval * 1000 * 1.1)
        if (self.__lastReceived > 0 and lost):
            logging.warning('Missing Detected!')
            miss = self.__missing.get()
            self.__missing.set(miss + 1)
            try:
                self.send_email_notification(
                    'Missing Data Alert',
                    f'Missing data detected. Packet ID: {packetId}'
                )
            except Exception as e:
                logging.error(f"Error sending email notification: {e}")
                messagebox.showerror("Notification Error", "Failed to send missing data alert email.")

        self.__lastReceived = packetId

        # Wild Data is not added to dataset
        if (newTemp < -40 or newTemp > 40):
            logging.warning('Wild Detected!')
            wild = self.__wild.get()
            self.__wild.set(wild + 1)
            try:
                self.send_email_notification(
                    'Wild Data Alert',
                    f'Wild data detected. Temperature: {newTemp}'
                )
            except Exception as e:
                logging.error(f"Error sending email notification: {e}")
                messagebox.showerror("Notification Error", "Failed to send wild data alert email.")
            return

        if(len(self.__data) >= 20):
            self.__data.pop(0)

        self.__data.append(newTemp)
        self.update_plot()

    def create_styles(self, parent=None):
        style = Style()
        style.configure('TFrame', background='#c8e6d3')
        style.configure('TLabel', background='#c8e6d3')
        style.configure('TCombobox', font=('Arial', 14))
        style.configure('TButton', font=('Arial', 14))

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
        Canvas(width=1060, height=680).pack()
        container = Frame(self, padding=(5, 5))
        container.place(relx=0.015, rely=0.02, relheight=0.96, relwidth=0.97)
        Label(container, text='Temperature Client', font='Arial 16 bold').place(relx=0.33, height=30)
        Label(container, text='PacketID: ', font='Arial 14').place(relx=0.7, rely=0.15)
        Label(container, textvariable=self.__packetId, font='Arial 14').place(relx=0.85, rely=0.15)
        Label(container, text='Name: ', font='Arial 14').place(relx=0.7, rely=0.25)
        Label(container, textvariable=self.__name, font='Arial 14').place(relx=0.85, rely=0.25)
        Label(container, text='IPv4: ', font='Arial 14').place(relx=0.7, rely=0.35)
        Label(container, textvariable=self.__ipv4, font='Arial 14').place(relx=0.85, rely=0.35)
        Label(container, text='Temperature: ', font='Arial 14').place(relx=0.7, rely=0.45)
        Label(container, textvariable=self.__temp, font='Arial 14').place(relx=0.85, rely=0.45)
        Label(container, text='Wild Data: ', font='Arial 14').place(relx=0.7, rely=0.55)
        Label(container, textvariable=self.__wild, font='Arial 14').place(relx=0.85, rely=0.55)
        Label(container, text='Missing: ', font='Arial 14').place(relx=0.7, rely=0.65)
        Label(container, textvariable=self.__missing, font='Arial 14').place(relx=0.85, rely=0.65)
        topicOptions = Combobox(container, values=self.__sensors_name, textvariable=self.__sensorName, width=15, style='TCombobox')
        topicOptions.place(relx=0.7, rely=0.82)
        topicOptions.current(0)

        self.startButton = Button(container, textvariable=self.__button_name, style='TButton', command=self.btn_on_click)
        self.startButton.place(relx=0.83, rely=0.82)


        # Initialize Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        self.ax.set_title("Temperature Data")
        self.ax.set_xlabel("Data Points")
        self.ax.set_ylabel("Temperature (°C)")
        self.line, = self.ax.plot([], [], 'r-')

        # Embed the plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().place(relx=0.05, rely=0.24, width=650, height=400)

        self.create_styles()

    def btn_on_click(self):
        if self.__button_name.get() == 'Start':
            # Set States
            self.__button_name.set('Stop')
            self.__data.clear()
            self.__lastReceived = -1
            self.__wild.set(0)
            self.__missing.set(0)
            try:
                # Connect to Mqtt broker on specified host and port
                self.__mqttc.connect(host='broker.hivemq.com', port=1883)
                self.__mqttc.loop_start()
                logging.info('Starting: %s', self.__sensorName.get())
            except Exception as e:
                logging.error(f"Error connecting to MQTT broker: {e}")
                messagebox.showerror("MQTT Connection Error", "Failed to connect to the MQTT broker.")
        else:
            self.__button_name.set('Start')
            try:
                self.__mqttc.unsubscribe(topic=self.__sensorName.get())
                self.__mqttc.loop_stop()
            except Exception as e:
                logging.error(f"Error unsubscribing from topic: {e}")
                messagebox.showerror("MQTT Error", "Failed to unsubscribe from the MQTT topic.")

    def on_connect(self, mqttc, userdata, flags, rc, properties=None):
        logging.info('Connected.. \n Return code: %s', str(rc))
        try:
            mqttc.subscribe(topic=self.__sensorName.get(), qos=0)
        except Exception as e:
            logging.error(f"Error subscribing to topic: {e}")
            messagebox.showerror("MQTT Subscription Error", "Failed to subscribe to the MQTT topic.")

    def on_message(self, mqttc, userdata, msg):
        try:
            message = json.loads(msg.payload)
            self.__packetId.set(message['packetId'])
            self.__name.set(message['name'])
            self.__temp.set(message['temp'])
            self.__ipv4.set(message['ipv4'])
            self.update_data(message['packetId'], message['interval'], message['temp'])
        except json.JSONDecodeError:
            logging.error('JSON Decode Error: Unable to decode the message payload.')
            messagebox.showerror("Data Error", "Failed to decode the received data.")
        except KeyError as e:
            logging.error(f"Missing key in JSON data: {e}")
            messagebox.showerror("Data Error", f"Received data is missing key: {e}")

    def on_subscribe(self, mqttc, userdata, mid, granted_qos, properties=None):
        logging.info('Subscribed')

    def update_plot(self):
        # Update plot with new data
        self.line.set_xdata(range(len(self.__data)))
        self.line.set_ydata(self.__data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
        self.canvas.draw()

    def simulate_missing_data(self, packetId):
        # Simulate occasional missing data by skipping data points
        if randint(0, 10) > 7:
            time.sleep(randint(1, 3))

if __name__ == '__main__':
    tempClient = TempClient()
    tempClient.mainloop()