from flask import Flask
from random import randint
from opentelemetry import trace, metrics
from azure.monitor.opentelemetry import configure_azure_monitor
import os

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter, AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)


from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter, 
)

from opentelemetry.sdk.trace import TracerProvider


exporter_metrics = AzureMonitorMetricExporter(connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] )

# ---- OTEL / App Insights (OK qui)
# configure_azure_monitor()

# ---- Flask app must be here, top-level
app = Flask(__name__)

provider = TracerProvider()

processor = BatchSpanProcessor(exporter) # this is for App Insights
# processor = BatchSpanProcessor(ConsoleSpanExporter()) # this is for console output

provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

# acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")

# acquire a meter
reader = PeriodicExportingMetricReader(exporter_metrics, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
meter = metrics.get_meter("diceroller")

roll_counter = meter.create_counter(
    "dice.rolls",
    description="Number of dice rolls"
)


def roll():
    # trace
    with tracer.start_as_current_span("roll", kind=trace.SpanKind.INTERNAL) as rollspan: #timer starts here
        # https://learn.microsoft.com/en-us/python/api/overview/azure/monitor-opentelemetry-exporter-readme?view=azure-python-preview
        result = randint(-2, 2)

        if result == 0: # 20% chance of error
            result = 10/0
        else:
            result = randint(10000, 10010)

        rollspan.set_attribute("roll.value", result)

        # metrics
        roll_counter.add(1, {"roll.value": result})

    return result

@app.route("/rolldice")
def roll_dice():
    return str(roll())


if __name__ == "__main__":
    app.run(port=8080)