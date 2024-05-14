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
	</p><br>
</div>

Table of contents:

- [1. Overview](#1-overview)
  - [1.1. Features](#11-features)
  - [1.2. Components](#12-components)
- [1.3. Tested environment](#13-tested-environment)
- [2. Quick start](#2-quick-start)
  - [2.1. Configure Ansible](#21-configure-ansible)
  - [2.2. Normal deployment](#22-normal-deployment)
  - [2.3. Containerize deployment](#23-containerize-deployment)
  - [2.4. Encrypting with `kriptyn`](#24-encrypting-with-kriptyn)
  - [2.5. Encrypting with `ansible-vault`](#25-encrypting-with-ansible-vault)
  - [2.6. **Last but not least**](#26-last-but-not-least)
- [3. Variables](#3-variables)
- [4. Contributors](#4-contributors)

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
- [Google Cadvisor](https://github.com/google/cadvisor)
- [Haproxy](http://www.haproxy.org/)
- [Keepalived](https://www.keepalived.org/)
- [Grafana](https://github.com/grafana/grafana)
- Other Prometheus exporters - **TODO**

## 1.3. Tested environment

- CentOS 7
- Ubuntu 22.04

## 2. Quick start

### 2.1. Configure Ansible

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

### 2.2. Normal deployment

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
7. Install dependencies

```shell
pip install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

8. Run [tools/ansitheus](./tools/ansitheus), figure out yourself:

```bash
Usage: ./tools/ansitheus COMMAND [option]

Options:
    --inventory, -i <inventory_path> Specify path to ansible inventory file
    --configdir, -c <config_path>    Specify path to directory with config.yml
    --verbose, -v                    Increase verbosity of ansible-playbook
    --tags, -t <tags>                Only run plays and tasks tagged with these values
    --limit <host>                   Specify host to run plays
    --help, -h                       Show this usage information
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

### 2.3. Containerize deployment

```bash
docker run --name ansitheus --rm -v /path/to/your/inventory:/etc/ansitheus/inventory \
    -v /path/to/your/config:/etc/ansitheus \
    -v /tmp/facts_cache:/tmp/facts_cache:rw \
    kiennt26/ansitheus:<version> -h

Usage: ./tools/ansitheus COMMAND [option]

Options:
    --inventory, -i <inventory_path> Specify path to ansible inventory file
    --configdir, -c <config_path>    Specify path to directory with config.yml
    --verbose, -v                    Increase verbosity of ansible-playbook
    --tags, -t <tags>                Only run plays and tasks tagged with these values
    --help, -h                       Show this usage information
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


### 2.4. Encrypting with `kriptyn`

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

### 2.5. Encrypting with `ansible-vault`

Encrypting config & inventory files with [`ansible-vault`](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

To encrypt `ansible-vault encrypt <file1> <file2> ...`, it will ask for an input as password

To view encrypted files `ansible-vault view <file_path>`, it will ask for password

To edit encrypted files `ansible-vault edit <file_path>`, it will ask for password

### 2.6. **Last but not least**

To run [tools/ansitheus](./tools/ansitheus) with encrypted files, please add `--ask-vault-pass` to command.

## 3. Variables

> **NOTE**:
>
> `keepalived_virtual_router_id` please be aware that this number should be unique among current SUBNET; otherwise, it will cause unexpected behaviors.

All variables can be overridden. Check out:
- [ansible/group_vars/all.yml](./ansible/group_vars/all.yml).
- Role variables which are stored in `ansible/roles/<role-name>/defaults/main.yml`.

## 4. Contributors

1. [Kien Nguyen](https://github.com/ntk148v)
2. [Dat Vu](https://github.com/vtdat)
3. [Duc Nguyen](https://github.com/vanduc95)
4. [Long Cao](https://github.com/LongCaoBK)
