# Target sharding for multi-node promnetheus deployment

## 1. Hashmod

`hashmod` is a built-in metrics filtering mechanism of Prometheus. In a multi-node Prometheus setup, we can use `hashmod` to distribute the target endpoints accross Promwetheus nodes, helping to reduce the workload of Prometheus instance on every nodes.

### 1.1 How it works

Each metric scraped by Prometheus has its own labels and values, `hashmod` uses these values to compute a `hash_value` for each metric given a defined `modulus` as described in [Hashing and Sharding on Label Values](https://training.promlabs.com/training/relabeling/writing-relabeling-rules/hashing-and-sharding-on-label-values/).

`hasmod` can be configured inside `relabel_configs` field in Prometheus configuration file `prometheus.yml` or service discovery files, depending on specific setup.

Example configuration:
```yaml
relabel_configs:
- action: hashmod
  modulus: 2
  source_labels:
  - __address__
  target_label: __tmp_hash__
```

The `hash_value` is assigned to the `__tmp_hash__` label after performing hashmod on the value of `__address__` label.

### 1.2 How we distribute targets

During Ansible execution, the number of Prometheus nodes and the index of each node is determined based on the inventory provided. We set `modulus = <number-of-prometheus-nodes>` and `regex = <index-of-current-node>` to assign targets to a Prometheus node only when the `hash_value` of that target matches the index of that node.

```yaml
relabel_configs:
- action: hashmod
  modulus: <number-of-prometheus-nodes>
  source_labels:
  - __address__
  target_label: __tmp_hash__
- action: keep
  regex: <index-of-current-node>
  source_labels:
  - __tmp_hash__
```

**Notes**  
We use *special insternal label* `__address__` and `__tmp_hash__`, which cause Prometheus to filter all metrics belonging to a target at once, as these labels are assigned to all metrics scraped from that target. Therefore, this allow filtering before scraping. The targets whose metrics are to be dropped will not be scraped.

## 2. Setup

> Sharding should only be enabled if Prometheus nodes are running in remote-write mode. It is incompatible with Prometheus running in HA mode, as metrics are distributed across Prometheus instances, and the master Prometheus node may not always contain the desired metrics.

To enable sharding, set variable `prometheus_enable_target_sharding: true` in ansible configuration file. 