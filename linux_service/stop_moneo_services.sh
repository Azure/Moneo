#!/bin/bash

systemctl stop moneo@node_exporter.service
systemctl stop moneo@net_exporter.service
systemctl stop moneo@nvidia_exporter.service
systemctl stop moneo_publisher.service
