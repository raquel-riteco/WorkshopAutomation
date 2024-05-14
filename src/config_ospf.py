import ipaddress
from nornir import InitNornir
from nornir.core.task import Result, Task
from nornir_jinja2.plugins.tasks import template_string
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_utils.plugins.functions import print_result

# TEMPLATE represents an option to manage multiple templates per platform
TEMPLATE_IFACE = {
    "eos": "interface Ethernet1\nip ospf network point-to-point",
}
TEMPLATE_OSPF = {
    "eos": "router ospf 1\npassive-interface default\nno passive-interface Ethernet1\nnetwork 0.0.0.0/0 area 0.0.0.0",
}


def config_task(task: Task, template) -> Result:
    """Nornir task that combines two subtasks:
    - Render a configuration from a Jinja2 template
    - Push the rendered configuration to the device
    """
    
    render_result = task.run(
        task=template_string,
        # The right template per platform is selected
        template=template[task.host.platform],
    )

    config_result = task.run(
        task=napalm_configure,
        # The rendered configuration from previous subtask is used
        # as the configuration input
        configuration=render_result.result,
        # dry_run means the changes without applying them
        dry_run=True,
    )

    return Result(host=task.host, result=config_result)


# Initialize Nornir inventory from a file
nr = InitNornir(config_file="config.yaml")

result_1 = nr.run(
    task=config_task,
    template=TEMPLATE_IFACE,
)
result_2 = nr.run(
    task=config_task,
    template=TEMPLATE_OSPF,
)

print_result(result_1)
print_result(result_2)
