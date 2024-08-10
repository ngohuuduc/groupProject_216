import os
import threading

scripts = [
  'python group_5_publisher.py --topic="sensor1"',
  'python group_5_publisher.py --topic="sensor2"',
  'python group_5_publisher.py --topic="sensor3"',
  'python group_5_subscriber.py',
  'python group_5_subscriber.py'
]

threads = []

if __name__ == '__main__':
  print(scripts)
  for script in scripts:
    print(script)
    thread = threading.Thread(target=os.system, args=[script])
    thread.setDaemon(True)
    thread.start()
    threads.append(thread)

  for thread in threads:
    thread.join()
  
  print('Exiting')