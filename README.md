<div align="center">
	<h1>Ansitheus</h1>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Ansible_logo.svg/1664px-Ansible_logo.svg.png" width="10%" height="10%">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Prometheus_software_logo.svg/2066px-Prometheus_software_logo.svg.png" width="10%" height="10%">
    <hr/>
	<p>
		<a href="https://github.com/ntk148v/ansitheus/blob/master/LICENSE">
			<img alt="GitHub license" src="https://img.shields.io/github/license/ntk148v/ansitheus?style=for-the-badge">
		</a>
		<a href="https://github.com/ntk148v/ansitheus/stargazers">
            <img alt="GitHub stars" src="https://img.shields.io/github/stars/ntk148v/ansitheus?style=for-the-badge">
        </a>
        <a href="https://github.com/ntk148v/ansitheus/tags">
            <img alt="Github tag" src="https://img.shields.io/github/tag/ntk148v/ansitheus?style=for-the-badge">
        </a>
        <a href="https://hub.docker.com/r/kiennt26/ansitheus/tags">
            <img alt="Docker tag" src="https://img.shields.io/docker/v/kiennt26/ansitheus?style=for-the-badge">
        </a>
	</p><br>
</div>

Table of contents:

- [1. Overview](#1-overview)
  - [1.1. Features](#11-features)
  - [1.2. Components](#12-components)
  - [1.3. Tested environment](#13-tested-environment)
- [2. Documentation](#2-documentation)
- [3. Contributors](#3-contributors)

## 1. Overview

Ansitheus's mission is to provide production-ready **containers** and deployment tools for operating [Prometheus](https://github.com/prometheus/prometheus) monitoring system. Ansitheus is highly opinionated out of the box, but allows for complete customization. This permits operators with minimal experience to deploy Prometheus quickly and as experience grows modify the Prometheus configuration to suit the operator’s exact requirements.

It is highly inspired by [kolla-ansible](https://docs.openstack.org/kolla-ansible).

If you want to deploy Prometheus monitoring system as systemd service, you may want to take a look at [Ansible Collection for Prometheus](https://github.com/prometheus-community/ansible).

### 1.1. Features

- Allow to configure & setup the system from scratch (prepare local repostiory, install necessary packages, configure Docker daemon...).
- Deploy & configure full [Prometheus](https://github.com/prometheus/prometheus) monitoring system using [Ansible](https://www.ansible.com/).
- Containerize Prometheus components.
- Support flexible High-availability deployment.
  - You can deploy mutiple Prometheus instances.
  - Sometimes Prometheus scrape process can cause high load on the target. Therefore, it should be only one instance scrape at time. Ansitheus supports us to deploy "stand-by" Prometheus instance which is only started if the "primary" instance was down.
- Highly flexible & configurable components.
- Support Docker private registry.
- Support Ansible vault.

### 1.2. Components

Ansitheus allows users to configure & deploy the following components:

- [Prometheus Server](https://github.com/prometheus/prometheus)
- [Prometheus Alertmanager](https://github.com/prometheus/alertmanager)
- [Prometheus Node-exporter](https://github.com/prometheus/node_exporter)
- [Prometheus Mysqld-exporter](https://github.com/prometheus/mysqld_exporter)
- [Prometheus Openstack-exporter](https://github.com/openstack-exporter/openstack-exporter)
- [Google Cadvisor](https://github.com/google/cadvisor)
- [Prometheus Nginx-exporter](https://github.com/nginx/nginx-prometheus-exporter)
- [Haproxy](http://www.haproxy.org/)
- [Keepalived](https://www.keepalived.org/)
- [Grafana](https://github.com/grafana/grafana)
- Other Prometheus exporters - **TODO**

### 1.3. Tested environment

- CentOS 7
- Ubuntu 22.04

## 2. Documentation

- Deployment philosophy: Ansitheus shares the same [philosophy with Kolla-ansible](https://docs.openstack.org/kolla-ansible/latest/admin/deployment-philosophy.html).
- [Quickstart](./docs/quickstart.md).
- [Troubleshooting guide](./docs/troubleshoot.md).

## 3. Contributors

1. [Kien Nguyen](https://github.com/ntk148v)
2. [Dat Vu](https://github.com/vtdat)
3. [Duc Nguyen](https://github.com/vanduc95)
4. [Long Cao](https://github.com/LongCaoBK)
