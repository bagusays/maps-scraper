import pika
import time
import pandas as pd

connection = pika.BlockingConnection(pika.ConnectionParameters(host="172.18.0.2"))
channel = connection.channel()

channel.queue_declare(queue='coordinate')

df = pd.read_csv('coordinate.csv')

for index, row in df.iterrows():
    body = "{},{}".format(row["latitude"], row["longitude"])
    channel.basic_publish(exchange='', routing_key='coordinate', body=body)

    print("[x] {} Sent!".format(body))
    time.sleep(0.01)

connection.close()