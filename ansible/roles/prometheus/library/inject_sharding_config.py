from ansible.module_utils.basic import AnsibleModule
import yaml
import json
import os

def load_config_file(path):
    _, ext = os.path.splitext(path)
    if ext in ['.yaml', '.yml']:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)

def save_config_file(data, path):
    _, ext = os.path.splitext(path)
    if ext in ['.yaml', '.yml']:
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    elif ext == '.json':
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def add_sharding(config, modulus, hash_value, ignorances):
    for job in config.get('scrape_configs', []):
        if job.get('job_name', '') not in ignorances:
            job['relabel_configs'] = job.get('relabel_configs', [])
            job['relabel_configs'].extend([
                {
                    'source_labels': ['__address__'],
                    'modulus': modulus,
                    'target_label': '__hash_value',
                    'action': 'hashmod'
                },
                {
                    'source_labels': ['__hash_value'],
                    'regex': hash_value,
                    'action': 'keep'
                }
            ])
    return config

def main():
    module = AnsibleModule(
        argument_spec=dict(
            source=dict(type='str', required=True),
            modulus=dict(type='int', required=True),
            hash_value=dict(type='int', required=True),
            ignorances=dict(type='list', elements='str', required=True)
        )
    )

    source = module.params['source']
    modulus = module.params['modulus']
    hash_value = module.params['hash_value']
    ignorances = module.params['ignorances']

    config = load_config_file(source)
    if not isinstance(config, dict):
        module.exit_json(changed=False)
        return
    sharded_config = add_sharding(config, modulus, hash_value, ignorances)
    save_config_file(sharded_config, source)

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
