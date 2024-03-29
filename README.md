<div align="center">
	<h1>Ansitheus</h1>
	<blockquote align="center">Ansible + Prometheus = Ansitheus</blockquote>
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
	</p><br>
</div>

- [1. Description](#1-description)
- [2. Features](#2-features)
- [3. Components](#3-components)
- [4. Requirements](#4-requirements)
- [5. Tested environment](#5-tested-environment)
- [6. Role variables](#6-role-variables)
- [7. Configure Ansible](#7-configure-ansible)
- [8. Getting started](#8-getting-started)
  - [8.1. Basic](#81-basic)
  - [8.2. Docker](#82-docker)
  - [8.3. Encrypting with `kriptyn`](#83-encrypting-with-kriptyn)
  - [8.4. Encrypting with `ansible-vault`](#84-encrypting-with-ansible-vault)
  - [8.5. **Last but not least**](#85-last-but-not-least)
- [9. Contributors](#9-contributors)

## 1. Description

- Deploy & configure full [Prometheus](https://github.com/prometheus/prometheus) monitoring system using [Ansible](https://www.ansible.com/).
- Highly inspired by [kolla-ansible](https://docs.openstack.org/kolla-ansible).
- Components are deployed as [Docker](https://docker.com) container.

## 2. Features

- Allow to configure & setup the system from scratch (prepare local repostiory, install necessary packages, configure Docker daemon...).
- Deploy & configure full [Prometheus](https://github.com/prometheus/prometheus) monitoring system using [Ansible](https://www.ansible.com/).
- Containerize Prometheus components.
- Support High Availability.
- Support centralized Docker logging with Fluentd.
- Highly flexible & configurable components.
- Support Docker private registry.
- Support Ansible vault.

## 3. Components

Ansitheus allows users to configure & deploy the following components:

- [Prometheus Server](https://github.com/prometheus/prometheus)
- [Prometheus Alertmanager](https://github.com/prometheus/alertmanager)
- [Prometheus Node-exporter](https://github.com/prometheus/node_exporter)
- [Google Cadvisor](https://github.com/google/cadvisor)
- [Prometheus SNMP exporter](https://github.com/prometheus/snmp_exporter)
- [Haproxy](http://www.haproxy.org/)
- [Keepalived](https://www.keepalived.org/)
- [Fluentd](https://github.com/fluent/fluentd)
- [Grafana](https://github.com/grafana/grafana)
- Other Prometheus exporters - **TODO**

## 4. Requirements

Ansible >= 2.8.4 (It might work on previous versions, but we cannot guarantee it)

## 5. Tested environment

- CentOS 7

## 6. Role variables

> **NOTE**: TODO
>
> `keepalived_virtual_router_id` please be aware that this number should be unique among current SUBNET; otherwise, it will cause unexpected behaviors.

Check [ansible/group_vars/all.yml](./ansible/group_vars/all.yml) fir more details. We're too busy (& lazy) to create a table for it.

## 7. Configure Ansible

For best results, Ansible configuration should be tuned for your environment. For example, add the following options to the Ansible configuration file `/etc/ansible/ansible.cfg`:

```ini
[defaults]
deprecation_warnings=False
host_key_checking=False
pipelining=True
forks=100
gathering = smart
fact_caching = jsonfile
# Ansible should be run as root
fact_caching_connection = /etc/ansible/facts.d
retry_files_enabled = False
fact_caching_timeout = 0

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=900s
pipelining = True
```

Further information on tuning Ansible is available [here](https://www.ansible.com/blog/ansible-performance-tuning).

## 8. Getting started

### 8.1. Basic

1. Install Ansible in deployment node.

2. Clone this repostiory.

3. Create configuration directory, default path `/etc/ansitheus`.

   ```bash
   sudo mkdir -p /etc/ansitheus
   sudo chown $USER:$USER /etc/ansitheus
   ```

4. Copy `config.yml` to `/etc/ansitheus` directory - this is the main configuration for Ansible monitoring tool.

   ```bash
   cp /path/to/ansitheus/repository/etc/ansitheus/config.yml \
       /etc/ansitheus/config.yml
   ```

5. Copy inventory files to the current directory.

   ```bash
   cp /path/to/ansitheus/repository/ansible/inventory/* .
   ```

6. Modify inventory & `/etc/ansitheus/config.yml`.
7. Run [tools/ansitheus](./tools/ansitheus), figure out yourself:

```bash
Usage: ./tools/ansitheus COMMAND [option]

Options:
    --inventory, -i <inventory_path> Specify path to ansible inventory file
    --configdir, -c <config_path>    Specify path to directory with config.yml
    --verbose, -v                    Increase verbosity of ansible-playbook
    --tags, -t <tags>                Only run plays and tasks tagged with these values
    --limit <host>                   Specify host to run plays
    --help, -h                       Show this usage information
    --skip-common                    Skip common role
    --skip-gather-fact               Skip gather fact
    --ask-vault-pass                 Ask for vault password
    --vault-password-file            Provide the vault password file

Commands:
    precheck                         Do pre-deployment checks for hosts
    deploy                           Deploy and start all ansitheus containers
    pull                             Pull all images for containers (only pull, no running containers)
    destroy                          Destroy Prometheus containers and service configuration
                                        --include-images to also destroy Prometheus images
                                        --include-volumes to also destroy Prometheus volumes
```

### 8.2. Docker

If you don't to do clone step, install requirements,... you can run Ansitheus with Docker.

1. Pull or build image kiennt26/ansitheus:<version>. <version> is the ansitheus repository's tag.

2. Run it.

```bash
docker run --name ansitheus --rm -v /path/to/your/inventory:/etc/ansitheus/inventory \
    -v /path/to/your/config:/etc/ansitheus \
    -v /tmp/facts_cache:/tmp/facts_cache:rw \
    10.240.201.50:8890/cloudlab/ansitheus:<version> -h

Usage: ./tools/ansitheus COMMAND [option]

Options:
    --inventory, -i <inventory_path> Specify path to ansible inventory file
    --configdir, -c <config_path>    Specify path to directory with config.yml
    --verbose, -v                    Increase verbosity of ansible-playbook
    --tags, -t <tags>                Only run plays and tasks tagged with these values
    --help, -h                       Show this usage information
    --skip-common                    Skip common role
    --limit <host>                   Specify host to run plays
    --skip-gather-fact               Skip gather fact
    --ask-vault-pass                 Ask for vault password
    --vault-password-file            Provide the vault password file

Commands:
    precheck                         Do pre-deployment checks for hosts
    deploy                           Deploy and start all ansitheus containers
    pull                             Pull all images for containers (only pull, no running containers)
    destroy                          Destroy Prometheus containers and service configuration
                                        --include-images to also destroy Prometheus images
                                        --include-volumes to also destroy Prometheus volumes

```

### 8.3. Encrypting with `kriptyn`

In regard to security concern, password of encrypted files should be changed periodicallyl. However, the number of files needs encrypting might change depending on deployment node.

The need of mass encrypting/changing password emerges, `kriptyn` is there to save your day.

`kriptyn` supports encrypting, decrypting & rekeying for multiple files.

Try `./tools/kryptin` & provide it with filename or file pattern such as: `test.*`, `*.yml`, etc.

```bash
➜ ./tools/kriptyn
Usage: ./tools/kriptyn COMMAND [filename1] [filename2] ...

Commands:
    encrypt         Encrypt files
    decrypt         Decrypt files
    rekey           Encrypt files with new password
    help            Show this

```

**_Note_**:

- _only files in `/home`, `/etc`, `/root` are found_
- _`root` permission might required for files in `/etc` & `/root`_

### 8.4. Encrypting with `ansible-vault`

Encrypting config & inventory files with [`ansible-vault`](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

To encrypt `ansible-vault encrypt <file1> <file2> ...`, it will ask for an input as password

To view encrypted files `ansible-vault view <file_path>`, it will ask for password

To edit encrypted files `ansible-vault edit <file_path>`, it will ask for password

### 8.5. **Last but not least**

To run [tools/ansitheus](./tools/ansitheus) with encrypted files, please add `--ask-vault-pass` to command.

## 9. Contributors

1. [Kien Nguyen](https://github.com/ntk148v)
2. [Dat Vu](https://github.com/vtdat)
3. [Duc Nguyen](https://github.com/vanduc95)
4. [Long Cao](https://github.com/LongCaoBK)
