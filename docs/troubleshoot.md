# Troubleshooting Guide

## 1. Failures

If Ansitheus fails, you can add `-vvv` to provide more information (actually it's Ansible [verbose](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html) option).

The fastest way during to recover from a deployment failure is to remove the failed deployment:

```shell
./tools/ansitheus destroy -i <inventory-file>
```

## 2. Debugging

The status of containers after deployment can be determined on the deployment targets by executing:

```shell
docker ps -a
```

If any of the containers exited, this indicates a bug in the container. Check out the stdout logs:

```shell
docker logs <container-name>
```

To learn more about Docker command line operation please refer to [Docker documentation](https://docs.docker.com/reference/).