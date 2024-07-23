# Ansible Role: fluentd

Deploy [fluentd](https://www.fluentd.org/) using Ansible and Docker.

## Requirements

- Ansible >= 2.9 (It might work on previous versions, but we cannot guarantee it).

## Role variables

All variables which can be overridden are stored in [defaults/main.yml](./defaults/main.yml) file as well as in [meta/argument_specs.yml](./meta/argument_specs.yml).

## Example playbook

```yaml
- hosts: all
  roles:
      - { role: fluentd }
```
