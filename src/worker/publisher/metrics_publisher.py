import urllib
import socket
import json
import time
import shlex
import subprocess
import sys
from prometheus_client.parser import text_string_to_metric_families


publisher_agent = sys.argv[1]

if publisher_agent == 'geneva':
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, AggregationTemporality
    from opentelemetry.sdk.resources import Resource
elif publisher_agent == 'azure_monitor':
    from azure.monitor.opentelemetry import configure_azure_monitor
else:
    raise Exception('##[ERROR]Invalid publisher agent')

from opentelemetry import metrics
from opentelemetry.sdk.metrics import Counter, Histogram


def get_geneva_exporter_meter(metrics_auth, metrics_namespace):
    """
    Returns a meter that uses the OTLP exporter to send metrics to the collector
    Args:
        metrics_auth (str): The metrics auth
        metrics_namespace (str): The metrics namespace
    """
    resource = Resource(attributes={
        "microsoft_metrics_account": metrics_auth,
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


def get_azure_monitor_exporter_meter(metrics_auth, metrics_namespace):
    """
    Returns a meter that uses the Azure Monitor exporter to send metrics to the collector
    Args:
        metrics_auth (str): The metrics auth
        metrics_namespace (str): The metrics namespace
    """
    configure_azure_monitor(connection_string=metrics_auth)

    meter = metrics.get_meter_provider().get_meter(metrics_namespace)
    return meter


def shell_cmd(cmd, timeout):
    """
    Helper Function for running subprocess
    Args:
        cmd (str): The command to run
        timeout (int): The timeout for the command
    Returns:
        result (str): The result of the command
    """
    args = shlex.split(cmd)
    child = subprocess.Popen(args, start_new_session=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        result, _ = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        child.kill()
        print("##[ERROR]Command " + " ".join(args) + ", Failed on timeout")
        result = 'TimeOut'
        return result
    return result.decode()


def get_publisher_metrics_config():
    """
    Get the geneva metrics config
    Returns:
        config(dict): The geneva metrics configuration
    """
    with open('/tmp/moneo-worker/publisher/config/publisher_config.json') as f:
        config = json.load(f)
    return config


def get_vm_id():
    """
    Get the vm id
    Returns:
        vm_id(str): The vm id
    """
    cmd = 'curl -s -H Metadata:true \
    "http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-02-01&format=text"'
    vm_id = shell_cmd(cmd, 15).splitlines()[0]
    return vm_id


def get_scaleset_name():
    """
    Get the scaleset name
    Returns:
        scaleset_name(str): The scaleset name
    """
    cmd = 'curl -s -H Metadata:true \
    "http://169.254.169.254/metadata/instance/compute/name?api-version=2021-02-01&format=text"'
    scaleset_name = shell_cmd(cmd, 15).splitlines()[0]
    return scaleset_name.split("_")[0]


def get_subcription_id():
    """
    Get the subscription id
    Returns:
        subscription_id(str): The subscription id
    """
    cmd = 'curl -s -H Metadata:true \
    "http://169.254.169.254/metadata/instance/compute/subscriptionId?api-version=2021-02-01&format=text"'
    subscription_id = shell_cmd(cmd, 15).splitlines()[0]
    return subscription_id


class MetricsPublisher():
    """ MetricsPublisher is a class that using optl_exporter publishes metrics to Geneva"""
    def __init__(self, metrics_ports=None, metrics_auth=None, metrics_namespace=None):
        self.metrics_ports = metrics_ports
        self.metrics_auth = metrics_auth
        self.metrics_namespace = metrics_namespace
        self.node_name = socket.gethostname()
        self.vm_id = get_vm_id()
        self.scaleset_name = get_scaleset_name()
        if publisher_agent == 'geneva':
            self.meter = get_geneva_exporter_meter(self.metrics_auth, self.metrics_namespace)
        elif publisher_agent == 'azure_monitor':
            self.meter = get_azure_monitor_exporter_meter(self.metrics_auth, self.metrics_namespace)
        else:
            print("##[ERROR]Invalid publisher agent")
        self.metricNametoCounter = dict()
        self.metricNametoHistogram = dict()
        self.metricKeytoPreviousValue = dict()

    def get_metrics(self):
        """
        Get a list of metrics from the specified metrics ports
        Returns:
            metrics(list): A list of metrics:
            [{'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}]
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
                    metrics.append({'name': metric_name, 'value': metric_value,
                                    'labels': metric_labels, 'type': metric_type})
        return metrics

    def publish_metrics(self, metrics):
        """
        Publish the metrics to Geneva according to the metric type
        Args:
            metrics(list): A list of metrics:
            [{'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}]
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
            metric(dict): A metric dictionary:
            {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
        """
        metric_value = metric['value'] if metric['value'] is not None else 0
        key = self.get_key_from_metric(metric)
        if key not in self.metricKeytoPreviousValue:
            self.metricKeytoPreviousValue[key] = metric_value
            return
        previous_value = self.metricKeytoPreviousValue[key]
        self.metricKeytoPreviousValue[key] = metric_value
        delta = metric_value - previous_value
        # If the delta is negative, it means the counter has been reset
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
            metric(dict): A metric dictionary:
            {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
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
            metric(dict): A metric dictionary:
            {'name': metric_name, 'value': metric_value, 'labels': metric_labels, 'type': metric_type}
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
        tags['vm_id'] = self.vm_id
        tags['scaleset_name'] = self.scaleset_name
        for label in metric_labels:
            tags[label] = metric_labels[label]
        return tags


if __name__ == '__main__':
    # Get the publisher agent config
    agent_config = get_publisher_metrics_config()

    # Get common config
    metrics_ports = agent_config['common_config']['metrics_ports']
    metrics_namespace = agent_config['common_config']['metrics_namespace']
    interval = int(agent_config['common_config']['interval'])

    # Get publisher agent config
    if publisher_agent == 'geneva':
        metrics_auth = agent_config['geneva_agent_config']['metrics_account']
    elif publisher_agent == 'azure_monitor':
        metrics_auth = agent_config['azure_monitor_agent_config']['connection_string']
    else:
        raise Exception('##[ERROR]The publisher agent is not supported')

    # Start the publisher agent to publish metrics
    metricsPublisher = MetricsPublisher(
        metrics_ports=metrics_ports,
        metrics_auth=metrics_auth,
        metrics_namespace=metrics_namespace)

    # Publish metrics every 20 seconds
    while True:
        raw_metrics = metricsPublisher.get_metrics()
        metricsPublisher.publish_metrics(raw_metrics)
        time.sleep(interval)
