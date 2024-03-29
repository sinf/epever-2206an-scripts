import json
import time
from threading import Thread

from .util import *
from .register import *
from .device import *

def start_mqtt(the_device):
    import paho.mqtt.client as paho

    def mqtt_main():
        client = paho.Client(client_id="epever-modbus-client",
             protocol=paho.MQTTv5,
             callback_api_version=paho.CallbackAPIVersion.VERSION2)
        client.connect(config("mqtt.ip"), config("mqtt.port"))
        client.loop_start()
        while True:
            delay = config("mqtt.poll_delay_s",30)
            debug_print(f'mqtt: deciding whether to publish')
            now=time.time()
            the_device.read_regs(the_device.ids('stats'), update_older_than=now-delay)
            if regs := the_device.collect_for_push('mqtt', config('mqtt.max_publish_interval')):
                for reg in regs:
                    if reg.should_always_skip_logging() or reg.dtype == 'date_sm_hd_MY':
                        continue
                    j = json.dumps(reg.to_dict(), indent=1)
                    topic = config("mqtt.topic")+'/'+reg.name
                    debug_print(f'mqtt: publish {len(j)} B to {topic}')
                    client.publish(topic, payload=j, qos=0)
            time.sleep(delay)
    t=Thread(target=mqtt_main, daemon=True, name='mqtt-client')
    t.start()
    return t

