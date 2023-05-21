import random
import time
import json
import pandas as pd

import streamlit as st
from paho.mqtt import client as mqtt_client

BROKER_HOST    = "170.187.230.245"
BROKER_PORT    = 1883

_device        = "dev001"
_username      = "userdash"
_password      = "dashdashfish233!"
_client_id     = f"aris-dashboard-{random.randint(0, 1000)}"
_client        = mqtt_client.Client(_client_id)
_msg_payload   = list()

# Real-time Data Variables
_temperature  = float()
_turbidity    = float()
_pH           = float()
_conductivity = float()
_do           = float()

# Previous Data
_pv_temp      = float()
_pv_turb      = float()
_pv_ph        = float()
_pv_co        = float()
_pv_do        = float()

# Sensor Location
_sensor_id    = str()
_sensor_lc    = str()

def on_mqtt_message(client, userdata, msg):
    msg_string     = str(msg.payload.decode('utf-8'))
    _field, _tags  = json.loads(msg_string)

    global _temperature, _turbidity, _pH, _conductivity, _do
    global _pv_temp, _pv_turb, _pv_ph, _pv_co, _pv_do
    global _sensor_id, _sensor_lc

    _pv_temp       = round(_temperature, 2)
    _pv_turb       = round(_turbidity, 2)
    _pv_ph         = round(_pH, 2)
    _pv_co         = round(_conductivity, 2)
    _pv_do         = round(_do, 2)

    _temperature   = round(_field["temperature"], 2)
    _turbidity     = round(_field["turbidity"], 2)
    _pH            = round(_field["ph"], 2)
    _conductivity  = round(_field["conductivity"], 2)
    _do            = round(_field["do"], 2)

    _sensor_id     = _tags["sensor_id"]
    _sensor_lc     = _tags["location"]

def connect(client) -> None:
    client.username_pw_set(_username, _password)
    client.message_callback_add("/sensors/#", on_mqtt_message)
    client.connect(BROKER_HOST, BROKER_PORT)
    return None

def main() -> None:
    global _temperature
    global _turbidity
    global _pH
    global _conductivity
    global _do

    st.title("Real-time River Water Quality")
    dev_option  = st.selectbox(
        "Choose Topic",
        ("/sensors/mock", "/sensors/water/dev001")
    )

    placeholder = st.empty()

    connect(_client)
    _client.unsubscribe("/sensors/#")
    _client.subscribe(str(dev_option))

    while True:
        _client.loop()

        with placeholder.container():
            tu_metric, ph_metric = st.columns(2)
            co_metric, do_metric = st.columns(2)
            te_metric,         _ = st.columns(2)
            device_id, device_lc = st.columns(2)
            
            te_metric.metric(
                label="Temperature",
                value=f"{_temperature} °C",
                delta=round(_temperature - _pv_temp, 2)
            )

            tu_metric.metric(
                label="Turbidity",
                value=f"{_turbidity} NTU",
                delta=round(_turbidity - _pv_turb, 2)
            )

            ph_metric.metric(
                label="pH",
                value=f"{_pH}",
                delta=round(_pH - _pv_ph, 2)
            )

            co_metric.metric(
                label="Conductivity",
                value=f"{_conductivity} ms/cm",
                delta=round(_conductivity - _pv_co, 2)
            )

            do_metric.metric(
                label="Dissolved Oxygen",
                value=f"{_do} mg/L",
                delta=round(_do - _pv_do, 2)
            )

            device_id.markdown(f"#### ID : {_sensor_id}")
            device_lc.markdown(f"#### Location : {_sensor_lc}")


            time.sleep(2)
    return None

if __name__ == "__main__":
    main()
