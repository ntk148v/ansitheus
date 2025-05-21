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

def add_sharding(config, modulus, hash_value):
    for job in config.get('scrape_configs', []):
        job['relabel_configs'] = [
            {
                'source_labels': ['__address__'],
                'modulus': modulus,
                'target_label': '__tmp_hash__',
                'action': 'hashmod'
            },
            {
                'source_labels': ['__tmp_hash__'],
                'regex': hash_value,
                'action': 'keep'
            }
        ]
    return config

def main():
    module = AnsibleModule(
        argument_spec=dict(
            source=dict(type='str', required=True),
            modulus=dict(type='int', required=True),
            hash_value=dict(type='int', required=True)
        )
    )

    source = module.params['source']
    modulus = module.params['modulus']
    hash_value = module.params['hash_value']

    config = load_config_file(source)
    if not isinstance(config, dict):
        module.exit_json(changed=False)
        return
    sharded_config = add_sharding(config, modulus, hash_value)
    save_config_file(sharded_config, source)

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
