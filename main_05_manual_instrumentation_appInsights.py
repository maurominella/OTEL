from flask import Flask
from random import randint
from opentelemetry import trace, metrics
from azure.monitor.opentelemetry import configure_azure_monitor
import logging

# ---- OTEL / App Insights (OK qui)
configure_azure_monitor()

# ---- Flask app must be here, top-level
app = Flask(__name__)

logging.basicConfig(level=logging.WARNING)

# acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")

# acquire a meter
meter = metrics.get_meter("diceroller")

roll_counter = meter.create_counter(
    "dice.rolls",
    description="Number of dice rolls"
)

def roll():
    result = randint(-2, 2)

    # metrics
    roll_counter.add(1, {"roll.value": 10/result})

    # traces
    with tracer.start_as_current_span("roll") as rollspan:
        rollspan.set_attribute("roll.value", 10/result)

    return result

@app.route("/rolldice")
def roll_dice():
    return str(roll())


if __name__ == "__main__":
    app.run(port=8080)