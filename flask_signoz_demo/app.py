import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import time
import random
from config import config

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

import logging

# Add this near the top of your file, after the imports
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize tracing and an exporter that can send data to SigNoz
resource = Resource(attributes={
    "service.name": os.getenv("OTEL_SERVICE_NAME"),
    "application": os.getenv("OTEL_RESOURCE_ATTRIBUTES").split("=")[1]
})

# Configure the exporter to use the SigNoz Cloud endpoint and access token
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    headers=(("signoz-access-token", os.getenv("SIGNOZ_ACCESS_TOKEN")),)
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

# Instrument Flask
FlaskInstrumentor().instrument_app(app)

# Get a tracer
tracer = trace.get_tracer(__name__)

# Set up metrics
metric_exporter = OTLPMetricExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    headers=(("signoz-access-token", os.getenv("SIGNOZ_ACCESS_TOKEN")),)
)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15000)  # Export every 15 seconds
metric_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
set_meter_provider(metric_provider)

meter = get_meter_provider().get_meter("flask-app")

# Create metrics
request_counter = meter.create_counter(
    "flask_http_request_duration_seconds_count",
    description="Total number of requests",
)

error_counter = meter.create_counter(
    "flask_http_request_errors_total",
    description="Total number of errors",
)

request_duration = meter.create_histogram(
    "flask_http_request_duration_seconds",
    description="Duration of requests",
    unit="s",
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    request_duration.record(request_latency, {"path": request.path, "method": request.method, "status": str(response.status_code)})
    request_counter.add(1, {"path": request.path, "method": request.method, "status": str(response.status_code)})
    logger.debug(f"Recorded request duration: {request_latency} seconds for path: {request.path}, method: {request.method}, status: {response.status_code}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    error_counter.add(1, {"path": request.path, "method": request.method})
    app.logger.error(f"An error occurred: {str(e)}")
    return jsonify({"error": "An internal error occurred"}), 500

@app.route('/')
def home():
    test_counter = meter.create_counter(
        "test_counter",
        description="A test counter",
    )
    test_counter.add(1)
    return jsonify({"message": "Welcome to the Flask SigNoz Demo!"})

@app.route('/fast')
def fast():
    return jsonify({"message": "This is a fast response!"})

@app.route('/slow')
def slow():
    time.sleep(2)  # Artificial delay
    return jsonify({"message": "This is a slow response!"})

@app.route('/error')
def error():
    if random.random() < 0.5:
        raise Exception("Random error occurred!")
    return jsonify({"message": "No error this time!"})

if __name__ == '__main__':
    app.run(debug=True)