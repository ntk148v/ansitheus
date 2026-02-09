# Quick start

Table of contents:

- [Quick start](#quick-start)
  - [1. Recommended reading](#1-recommended-reading)
  - [2. Non-containerized setup](#2-non-containerized-setup)
  - [3. Containerized setup (Recommended)](#3-containerized-setup-recommended)
  - [4. Prepare initial configuration](#4-prepare-initial-configuration)
  - [5. Deployment](#5-deployment)
  - [6. Encryption](#6-encryption)
    - [6.1. Encrypting with `kriptyn`](#61-encrypting-with-kriptyn)
    - [6.2. Encrypting with `ansible-vault`](#62-encrypting-with-ansible-vault)
    - [6.3. Last but not least](#63-last-but-not-least)


This guide provides the step by step instructions to deploy Prometheus stack using Ansitheus on bare metal servers or virtual machines.

## 1. Recommended reading

It’s beneficial to learn basics of both [Ansible](https://docs.ansible.com/) and [Docker](https://docs.docker.com/) before running Ansitheus.

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

## 2. Non-containerized setup

Typically commands that use the system package manager in this section must be run with root privileges. It is generally recommended to use a virtual environment to install Ansitheus and its dependencies, to avoid conflicts with the system site packages.

1. For Debian or Ubuntu, update the package index:

```shell
sudo apt update
```

2. Install Python build dependencies:

```shell
sudo apt install git python3-dev libffi-dev gcc libssl-dev
```

3. Clone this repository:

```shell
git clone https://github.com/ntk148v/ansitheus.git
cd ansitheus
```

4. Install dependencies:

```shell
sudo apt install python3-venv
# Create virtual environment and activate it
python3 -m venv /path/to/venv
source /path/to/venv/bin/activate
pip install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

1. Run [tools/ansitheus](./tools/ansitheus):

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

6. Create the `/etc/ansitheus` directory:

```shell
sudo mkdir -p /etc/ansitheus
sudo chown $USER:$USER /etc/ansitheus
```

7. Copy `config.yml` to `/etc/ansitheus` directory:

```shell
cp -r etc/ansitheus/config.yml /etc/ansitheus
```

## 3. Containerized setup (Recommended)

You can use a ready Docker container to run Ansitheus:

```shell
docker run --name ansitheus --rm -v /path/to/your/inventory:/etc/ansitheus/inventory \
    -v /path/to/your/config:/etc/ansitheus \
    -v /tmp/facts_cache:/tmp/facts_cache:rw \
    kiennt26/ansitheus:latest -h

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

## 4. Prepare initial configuration

- **Inventory**: The next step is to prepare our inventory file. An inventory is an Ansible file where we specify hosts and the groups that they belong to. We can use this to define node roles and access credentials. Check out the sample inventory files [here](../ansible/inventory/).
- **config.yml**: This is the main configuration file for Ansitheus and per default stored in `/etc/ansitheus/config.yml` file. There are a few options that are required to deploy Ansitheus:
  - Networking: Ansitheus requires a few networking options to be set. We need to set network interfaces used by OpenStack.
    - First interface to set is "network_interface". This is the default interface for multiple management-type networks.

    ```yaml
    network_interface: "eth0"
    ```

    - Next we need to provide the VIP for the multi nodes deployment:

    ```yaml
    ansitheus_vip_address: "10.1.0.100"
    ```

  - Enable additional services: To enable/disable services, set `enable_*` to "yes/no" respectively.
  - Docker registry: By default, Ansitheus gets the images from Docker hub. If you want to use the private Docker registry, modify `docker_*` variables.
  - Image: You can change the Docker image version by setting `*_version` variables. This is used mostly in upgrade case. The current version is listed here:

  ```yaml
  prometheus_version: "3.9.1"
  alertmanager_version: "0.31.0"
  node_exporter_version: "1.10.2"
  cadvisor_version: "0.56.2"
  grafana_version: "12.3.2"
  haproxy_version: "lts-alpine"
  ```

  - All variables can be overridden. Check out:
    - [ansible/group_vars/all.yml](../ansible/group_vars/all.yml).
    - Role variables which are stored in `ansible/roles/<role-name>/defaults/main.yml`.

- **/etc/ansitheus/config**: Ansitheus automatically merges the configuration in `/etc/ansitheus/config` with the generated configuration to provide flexible way to configure. As an example, by default Ansitheus generates Prometheus configuration using a Jinja template. But in the real life scenario, there are many exporters that Ansitheus hasn't (and won't) supported yet. To achieve this, simply `mkdir -p /etc/ansitheus/config/prometheus/` and modify the file `/etc/ansitheus/config/prometheus/prometheus.yml` with the contents.

## 5. Deployment

After the configuration is set, we can proceed to the deployment phase:

```shell
./tool/ansitheus -i /etc/ansitheus/inventory precheck
./tool/ansitheus -i /etc/ansitheus/inventory deploy
```

## 6. Encryption

### 6.1. Encrypting with `kriptyn`

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

### 6.2. Encrypting with `ansible-vault`

Encrypting config & inventory files with [`ansible-vault`](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

To encrypt `ansible-vault encrypt <file1> <file2> ...`, it will ask for an input as password

To view encrypted files `ansible-vault view <file_path>`, it will ask for password

To edit encrypted files `ansible-vault edit <file_path>`, it will ask for password

### 6.3. Last but not least

To run [tools/ansitheus](./tools/ansitheus) with encrypted files, please add `--ask-vault-pass` to command.
