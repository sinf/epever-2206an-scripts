
import json

class DeviceConfig:
    def __init__(self, path):
        with open(path) as f:
            self.json = json.load(f)

    def regs(self):
        for section in self.json['registers'].values():
            for reg in section:
                if not reg.get('skip_db') and reg.get('table') != 'none' and not reg.get('write_only'):
                    reg['id'] = reg['id'].lower()
                    yield reg

dev_name='epever2206an-1'
topic_prefix='iot/epever2206an-1/'
dev=DeviceConfig('config/mppt-device.json')

#### in main config, insert:
# mqtt: !include homeassistant-sensors.yaml

with open('homeassistant-sensors.yaml', 'w') as f:
    print("  sensor:", file=f)
    for r in dev.regs():
        id=r['id']
        name=r['name']
        ha_entity_id = f'sensor.{dev_name}.{name}'
        topic = topic_prefix + id
        unit = r.get('unit')

        print(f"""
    - name: '{name}'
      unique_id: 'sensor.{dev_name}.{name}'
      state_topic: '{topic}'
      value_template: '{{{{ value_json.value }}}}'
      device:
        name: 'Epever2206an'
        identifiers:
          - '{dev_name}'""", file=f)
        if unit:
            print(f"""\
      unit_of_measurement: '{unit}'""", file=f)

