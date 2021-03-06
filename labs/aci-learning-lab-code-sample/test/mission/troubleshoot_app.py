#!usr/bin/env python
import time
import argparse
from credentials import *
from acitoolkit.acitoolkit import *
from acitoolkit.aciFaults import Faults

cli_args = argparse.ArgumentParser("Troubleshoot Appliction", "Prints information useful to troubleshooting Application Issues")
cli_args.add_argument('-a', '--app', required=True,
                      help="The Application experiencing issues.")
cli_args.add_argument('-t', '--tenant', required=True,
                      help="The App's parent Tenant.")

args = cli_args.parse_args()
APP = vars(args)["app"]
TENANT = vars(args)["tenant"]

def main():
    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    print_app_health(session, TENANT, APP)
    print_app_faults(session, TENANT)
    print_tables(session, TENANT, APP)


def print_app_health(apic_session, tenant_name, app_name):
    """
    Function used to subscribe to an Application's Health subtree, and print
    back the Health Score for the given Application. The Tenant that the
    Application resides is required to uniquely identify the Application.

    :param apic_session: A Session Object that has passed authentication.
    :param tenant_name: The Tenant name that the Application belongs to.
    :param app_name: The Application Name

    :return: None
    """
    extension = '&rsp-subtree-include=health,no-scoped'
    tenant = Tenant(tenant_name)
    app = AppProfile(app_name, tenant)
    app.subscribe(apic_session, extension)

    print("\n{:<50}{}".format("Application", "Current Health"))
    print("{:<50}{}".format("-------------", "----------------"))
    
    while app.has_events(apic_session, extension):
            health_object = app.get_fault(apic_session, extension)
            health_inst = health_object['healthInst']['attributes']
            if health_inst['dn'] == "uni/tn-{}/ap-{}/health".format(tenant_name, app_name):
                tenant_app_name = "{}/{}".format(tenant, app)
                health = health_inst['cur']
                print("{:<50}{}\n".format(tenant_app_name, int(health)))
                time.sleep(5)


def print_app_faults(apic_session, tenant_name):
    """
    Function to subscribe to faults on the APIC, and print back only
    the one's associated to the specified Tenant.

    :param apic_session: A Session Object that has passed authentication.
    :param tenant_name: The Tenant name that the Application belongs to.

    :return: None
    """
    faults_instance = Faults()
    filter = {"domain": ["tenant", "infra"]}
    faults_instance.subscribe_faults(apic_session, filter)

    print("\nFAULTS:")

    while faults_instance.has_faults(apic_session, filter):
        faults = faults_instance.get_faults(apic_session, filter, tenant_name)
        if faults is not None:
            for fault in faults:
                if fault.severity != "warning" and fault.severity != "cleared":
                    print("----------------------------------------")
                    print("\nDescription: {}\n\nDN: {}\n\nRule: {}\n\nDomain: {}\n\nType: {}\n\nSeverity: {}".format(
                    fault.descr, fault.dn, fault.rule, fault.domain, fault.type, fault.severity))
                    time.sleep(5)


def print_tables(apic_session, tenant_name, app_name):
    """
    Function is used to collect a list of EPGs for the provided Application in the given Tenant. It then uses the EPG list to call the print_epg_table and print_endpoint_table functions.

    :param apic_session: A Session Object that has passed authentication.
    :param tenant_name: The Tenant name that the Application belongs to.
    :param app_name: The Application Name

    :return: None
    """
    tenant = Tenant.get_deep(apic_session, [tenant_name])[0]
    tenant_children = tenant.populate_children()
    # app = filter(lambda child: child.name == app_name, tenant_children)[0]
    app = [child for child in tenant_children if child.name == app_name][0] 
    app_children = app.populate_children()

    print("\nTIP: Check that each EPG is providing and consuming the correct Contracts")
    print_epg_table(app_children, app_name)

    print("\nTIP: Validate that the corect VLANs are assigned and that hosts are in the correct EPG")
    print_endpoint_table(app_children, app_name)


def print_epg_table(app_children_objects, app_name):
    """
    Function used to print a table of EPG attributes for an application.

    :param app_children_objects: A list of EPGs for an Application
    :param app_name: The Application Name

    :return: None
    """
    tables = EPG.get_table(app_children_objects, "{} ".format(app_name))
    text_string = ""
    for table in tables:
        text_string += table.get_text(tablefmt='fancy_grid') + '\n'
    
    print(text_string)

    time.sleep(5)


def print_endpoint_table(app_children_objects, app_name):
    """
    Function used to print a table of Endpoint attributes for an application.

    :param app_children_objects: A list of EPGs for an Application
    :param app_name: The Application Name

    :return: None
    """
    endpoint_list = []
    for epg in app_children_objects:
        endpoint_list.extend(epg.get_children(Endpoint))
    
    text_string = ""
    tables = Endpoint.get_table(endpoint_list, "{} ".format(app_name))
    for table in tables:
        text_string += table.get_text(tablefmt='fancy_grid') + '\n'
    
    print(text_string)


if __name__ == "__main__":
	main()