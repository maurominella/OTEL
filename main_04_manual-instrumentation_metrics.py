from random import randint
from flask import Flask, request
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
import logging

# ---- METRICS SETUP (FORCE EXPORT EVERY 5s) -------------------------------
reader = PeriodicExportingMetricReader(
    ConsoleMetricExporter(),
    export_interval_millis=5000,  # 5 seconds
)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("diceroller.meter")
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of dice rolls by value",
)

# ---- FLASK APP -----------------------------------------------------------
app = Flask(__name__)

# Reduce logging noise
logging.basicConfig(level=logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

i = 0

def roll():
    global i
    result = randint(1, 6)
    i += 1
    roll_counter.add(i, {"roll.value": result})
    return result

@app.route("/rolldice")
def roll_dice():
    result = roll()
    return str(result)