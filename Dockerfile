FROM python
WORKDIR /project/src
ADD . /project
ENV MQTT_SERVER $MQTT_SERVER
RUN pip install -r /project/requirements.txt
CMD ["python","app.py"]

# docker image build -t mu-mqtt .
# docker run -p 5001:5000 -e MQTT_SERVER='localhost' -d mu-mqtt
# docker run -p 5001:5000 -e MQTT_SERVER='192.168.0.6' -d mu-mqtt