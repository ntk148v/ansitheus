from ansible.module_utils.basic import AnsibleModule
import yaml
import os

def load_config_file(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def save_config_file(data, path):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def add_sharding(config, modulus, hash_value):
    if 'scrape_configs' in config.keys():
        for job in config['scrape_configs']:
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
    sharded_config = add_sharding(config, modulus, hash_value)

    save_config_file(sharded_config, source)
    module.exit_json(changed=True, msg='Sharding configurations added')

if __name__ == '__main__':
    main()