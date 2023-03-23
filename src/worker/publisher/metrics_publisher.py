import urllib
import socket
import json
import sched
import time
from prometheus_client.parser import text_string_to_metric_families

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider, Counter, Histogram
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, AggregationTemporality
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def get_optl_exporter_meter(metrics_account, metrics_namespace):
    """
    Returns a meter that uses the OTLP exporter to send metrics to the collector
    Args:
        metrics_account (str): The metrics account
        metrics_namespace (str): The metrics namespace
    """
    resource = Resource(attributes={
        "microsoft_metrics_account": metrics_account,
        "microsoft_metrics_namespace": metrics_namespace
    })

    temporality_delta = {Counter: AggregationTemporality.DELTA, Histogram: AggregationTemporality.DELTA}
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint="0.0.0.0:4317",
            insecure=True,
            preferred_temporality=temporality_delta)
    )

    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    meter = metrics.get_meter(__name__)
    return meter

def get_geneva_metrics_config():
    """
    Get the geneva metrics config
    Returns:
        config(dict): The geneva metrics configuration
    """

    with open('../install/config/geneva_config.json') as f:
        config = json.load(f)
    return config

class MetricsPublisher():
    """ MetricsPublisher is a class that using optl_exporter publishes metrics to Geneva"""
    def __init__(self, metrics_ports=None, metrics_account=None, metrics_namespace=None):
        self.metrics_ports = metrics_ports
        self.metrics_account = metrics_account
        self.metrics_namespace = metrics_namespace
        self.node_name = socket.gethostname()
        self.meter = get_optl_exporter_meter(self.metrics_account, self.metrics_namespace)
        self.metricNametoCounter = dict()
        self.metricNametoHistogram = dict()
        self.metricKeytoPreviousValue = dict()

    def get_metrics(self):
        """
        Get a list of metrics from the specified metrics ports
        Returns:
            metrics(list): A list of metrics: [{'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}]
        """
        metrics = []
        metrics_port_list = self.metrics_ports.split(',')
        for port in metrics_port_list:
            metrics_url = f"http://localhost:{port}/metrics"
            response = urllib.request.urlopen(metrics_url)
            content = response.read().decode('utf-8')
            metric_families = text_string_to_metric_families(content)
            for metric_family in metric_families:
                metric_type = metric_family.type
                for sample in metric_family.samples:
                    metric_name = sample.name
                    metric_value = sample.value
                    metric_labels = sample.labels
                    metrics.append({'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type})
        return metrics

    def publish_metrics(self, metrics):
        """
        Publish the metrics to Geneva according to the metric type
        Args:
            metrics(list): A list of metrics: [{'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}]
        """
        if metrics == {}:
            return
        for metric in metrics:
            if metric['type'] == 'counter':
                self.publish_counter(metric)
            elif metric['type'] == 'gauge':
                self.publish_gauge(metric)
            else:
                print('This metrics type is not supported')

    def publish_counter(self, metric):
        """
        Publish counter type metrics to Geneva
        Args:
            metric(dict): A metric dictionary: {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
        """
        metric_value = metric['value'] if metric['value'] is not None else 0
        key = self.get_key_from_metric(metric)
        if key not in self.metricKeytoPreviousValue:
            self.metricKeytoPreviousValue[key] = metric_value
            return
        
        previous_value = self.metricKeytoPreviousValue[key]
        self.metricKeytoPreviousValue[key] = metric_value
        delta = metric_value - previous_value

        if delta < 0:
            return
        
        if metric['name'] not in self.metricNametoCounter:
            self.metricNametoCounter[metric['name']] = self.meter.create_counter(metric['name'])
        counter = self.metricNametoCounter[metric['name']]
        tags = self.get_tags_from_metric(metric['labels'])
        counter.add(metric_value, tags)

    def publish_gauge(self, metric):
        """
        Publish gauge type metrics to Geneva
        Args:
            metric(dict): A metric dictionary: {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
        """
        if metric['name'] not in self.metricNametoHistogram:
            self.metricNametoHistogram[metric['name']] = self.meter.create_histogram(metric['name'])

        histogram = self.metricNametoHistogram[metric['name']]
        metric_value = float(metric['value']) if metric['value'] is not None else 0
        tags = self.get_tags_from_metric(metric['labels'])
        histogram.record(metric_value, tags)

    def get_key_from_metric(self, metric):
        """
        Get a unique key for the metric
        Args:
            metric(dict): A metric dictionary: {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
        Returns:
            key(str): A unique key for the metric ({metric_name}:{label_name}:{label_value})
        """
        key = ''
        key += metric['name']
        for label in metric['labels']:
            key += ':'
            key += label + ':' + metric['labels'][label]
        return key

    def get_tags_from_metric(self, metric_labels):
        """
        Get the tags from the metric labels
        Args:
            metric_labels(dict): A dictionary of metric labels: {label_name: label_value}
        Returns:
            tags(dict): A dictionary of tags: {tag_name: tag_value}
        """
        tags = {}
        tags['node_name'] = self.node_name
        for label in metric_labels:
            tags[label] = metric_labels[label]
        return tags

if __name__ == '__main__':
    # config = get_geneva_metrics_config()
    metrics_ports = '8000,8001,8002'
    metrics_account = 'moneo'
    metrics_namespace = 'MetricsPublisherV0'
    metricsPublisher = MetricsPublisher(metrics_ports=metrics_ports, metrics_account=metrics_account, metrics_namespace=metrics_namespace)
    while True:
        raw_metrics = metricsPublisher.get_metrics()
        metricsPublisher.publish_metrics(raw_metrics)
        time.sleep(20)
