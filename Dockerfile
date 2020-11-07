FROM python
WORKDIR /project
ADD . /project
RUN pip install -r /project/requirements.txt
CMD ["python","wsgi.py"]

# docker image build -t mu-mqtt .
# docker run -p 5001:5000 -e MQTT_SERVER='localhost' -d mu-mqtt
# docker run -p 5001:5000 -e MQTT_SERVER='192.168.0.6' -d mu-mqtt