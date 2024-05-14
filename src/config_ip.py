from nornir import InitNornir
import ipaddress
from nornir.core.task import Result, Task
from nornir_jinja2.plugins.tasks import template_string
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_utils.plugins.functions import print_result



# TEMPLATE represents an option to manage multiple templates per platform
TEMPLATE_ETH = {
    "eos": "interface Ethernet1\nno switchport\nip address {{ ip_address }}\nno shutdown",
}
TEMPLATE_LO = {
    "eos": "interface Loopback0\nip address {{ ip_address }}\nno shutdown",
}


def get_my_interface_ip(task: Task, host_id: int) -> Result:
    ip_network = ipaddress.IPv4Network(task.host["network"])

    for count, ip_address in enumerate(ip_network):
        if host_id == count or host_id == count:
            break
    else:
        raise ValueError("Only host IDs 1 and 2 are supported")

    return Result(
        host=task.host,
        result=ipaddress.IPv4Interface(f"{ip_address}/{ip_network.prefixlen}"),
    )


def set_eth_ip(task: Task, template) -> Result:
    """Nornir task that combines two subtasks:
    - Render a configuration from a Jinja2 template
    - Push the rendered configuration to the device
    """
    result_ip = task.run(
        task=get_my_interface_ip, host_id=1 if task.host.name == "router1" else 2
    )

    render_result = task.run(
        task=template_string,
        # The right template per platform is selected
        template=template[task.host.platform],
        ip_address=str(result_ip.result),
    )

    config_result = task.run(
        task=napalm_configure,
        # The rendered configuration from previous subtask is used
        # as the configuration input
        configuration=render_result.result,
    )

    return Result(host=task.host, result=config_result)



def set_lo_ip(task: Task, template) -> Result:
    """Nornir task that combines two subtasks:
    - Render a configuration from a Jinja2 template
    - Push the rendered configuration to the device
    """
    result_ip = "1.1.1.1/32" if task.host.name == "router1" else "1.1.1.2/32"

    render_result = task.run(
        task=template_string,
        # The right template per platform is selected
        template=template[task.host.platform],
        ip_address=result_ip,
    )

    config_result = task.run(
        task=napalm_configure,
        # The rendered configuration from previous subtask is used
        # as the configuration input
        configuration=render_result.result,
    )

    return Result(host=task.host, result=config_result)


# Initialize Nornir inventory from a file
nr = InitNornir(config_file="config.yaml")

result = nr.run(
    task=set_eth_ip,
    template=TEMPLATE_ETH,
)

print_result(result)

result = nr.run(
    task=set_lo_ip,
    template=TEMPLATE_LO,
)

print_result(result)


