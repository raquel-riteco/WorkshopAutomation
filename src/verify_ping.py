from nornir_napalm.plugins.tasks import napalm_ping
from nornir_utils.plugins.functions import print_result
from nornir import InitNornir


nr = InitNornir(config_file="config.yaml")

result_r1 = nr.filter(name="router1").run(task=napalm_ping, dest="1.1.1.2")
result_r2 = nr.filter(name="router2").run(task=napalm_ping, dest="1.1.1.1")

print_result(result_r1)
print_result(result_r2)


