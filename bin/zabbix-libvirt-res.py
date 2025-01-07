#!/opt/venvs/zabbix_env/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import json
import argparse

try:
    import libvirt
except ModuleNotFoundError as e:
    print("Python module libvirt is most likely not installed, Please install python-libvirt", file=sys.stderr)
    sys.exit(1)

def main():
    args = parse_args()
    if args.resource == "pool":
        if args.action == "list":
            pool = Pool(uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = json.dumps(list_to_zbx(pool.list(), '{#POOLNAME}'), sort_keys=True, indent=2)
        elif args.action == "count_active":
            pool = Pool(uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(pool.list(active=True))
        elif args.action == "count_inactive":
            pool = Pool(uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(pool.list(active=False))
        elif args.action == "total":
            pool = Pool(args.pool,uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = pool.size['total']
        elif args.action == "used":
            pool = Pool(args.pool,uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = pool.size['used']
        elif args.action == "free":
            pool = Pool(args.pool,uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = pool.size['free']
        elif args.action == "active":
            pool = Pool(args.pool,uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = pool.isactive
        elif args.action == "UUID":
            pool = Pool(args.pool,uri=args.uri)
            is_none(pool.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = pool.uuid
        pool.disconnect()

    elif args.resource == "net":
        if args.action == "list":
            net = Net(uri=args.uri)
            is_none(net.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = json.dumps(list_to_zbx(net.list(), '{#NETNAME}'), sort_keys=True, indent=2)
        elif args.action == "count_active":
            net = Net(uri=args.uri)
            is_none(net.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(net.list(active=True))
        elif args.action == "count_inactive":
            net = Net(uri=args.uri)
            is_none(net.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(net.list(active=False))
        elif args.action == "active":
            net = Net(args.net,uri=args.uri)
            is_none(net.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = net.isactive
        elif args.action == "UUID":
            net = Net(args.net,uri=args.uri)
            is_none(net.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = net.uuid
        net.disconnect()

    elif args.resource == "domain":
        if args.action == "list":
            dom = Domain(uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = json.dumps(list_to_zbx(dom.list(), '{#DOMAINNAME}'), sort_keys=True, indent=2)
        elif args.action == "count_active":
            dom = Domain(uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(dom.list(active=True))
        elif args.action == "count_inactive":
            dom = Domain(uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = len(dom.list(active=False))
        elif args.action == "active":
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.isactive
        elif args.action == "UUID":
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.uuid
        elif args.action == 'vcpus_current':
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.vcpus['current']
        elif args.action == 'vcpus_max':
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.vcpus['max']
        elif args.action == 'memory_current':
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.memory['current']
        elif args.action == "memory_usage":
            dom = Domain(args.domain, uri=args.uri)
            is_none(dom.conn, "Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.get_memory_usage()
        elif args.action == "cpu_usage":
            dom = Domain(args.domain, uri=args.uri)
            is_none(dom.conn, "Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.get_domain_cpu_usage()
        elif args.action == 'memory_max':
            dom = Domain(args.domain,uri=args.uri)
            is_none(dom.conn,"Could not connect to KVM using '%s'." % args.uri, 2)
            r = dom.memory['max']
        dom.disconnect()

    elif args.resource == "host":
        host = Host(uri=args.uri)
        is_none(host.conn, "Could not connect to KVM using '%s'." % args.uri, 2)

        if args.action == "version":
            r = host.version
        elif args.action == "type":
            r = host.type
        elif args.action == "cpu_usage":
            r = host.get_cpu_usage()
        elif args.action == "memory_usage":
            r = host.get_memory_usage()

        host.disconnect()

    print(r)

class Libvirt(object):
    def __init__(self, uri='qemu:///system'):
        self.uri = uri
        self.conn = None
        self.connect()
        if self.conn is not None and self.name is not None:
            self.get_info()

    def get_info(self):
        self.version = self.conn.getVersion()
        self.type = self.conn.getType()
        return None
    
    def connect(self, uri = None):
        if uri is None:
            uri = self.uri
        try:
            self.conn = libvirt.openReadOnly(uri)
        except:
            print("There was an error connecting to the local libvirt daemon using '%s'." % uri, file=sys.stderr)
            self.conn = None
        return self.conn

    def disconnect(self):
        return self.conn.close()

class Host(Libvirt):
    def __init__(self, uri='qemu:///system'):
        self.name = 'n/a'
        super(self.__class__, self).__init__(uri)

    def get_info(self):
        self.version = self.conn.getVersion()
        self.type = self.conn.getType()
        return None

    def get_cpu_usage(self, interval=1):
        """
        Retorna o uso de CPU do host em porcentagem (0 a 100).
        """
        try:
            # Coleta inicial de estatísticas de CPU
            cpu_stats_1 = self.conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS, 0)
            if not cpu_stats_1:
                raise Exception("Failed to retrieve initial CPU stats")

            total_time_1 = sum(cpu_stats_1.values())
            idle_time_1 = cpu_stats_1.get('idle', 0)

            import time
            time.sleep(interval)  # Espera pelo intervalo definido

            # Coleta final de estatísticas de CPU
            cpu_stats_2 = self.conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS, 0)
            if not cpu_stats_2:
                raise Exception("Failed to retrieve final CPU stats")

            total_time_2 = sum(cpu_stats_2.values())
            idle_time_2 = cpu_stats_2.get('idle', 0)

            # Calcula a diferença entre os tempos total e ocioso
            total_diff = total_time_2 - total_time_1
            idle_diff = idle_time_2 - idle_time_1

            if total_diff == 0:
                raise Exception("Total time difference is zero, unable to calculate CPU usage")

            # Calcula o uso de CPU
            cpu_usage = ((total_diff - idle_diff) / total_diff) * 100
            return round(cpu_usage, 2)

        except libvirt.libvirtError as e:
            print(f"Failed to retrieve CPU stats: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error calculating CPU usage: {e}", file=sys.stderr)
            sys.exit(3)

    def get_memory_usage(self):
        """
        Retorna o uso de memória do domínio ou do host em porcentagem (0 a 100) e em bytes.
        """
        try:
            if hasattr(self, 'name') and self.name != 'n/a':  # Verifica se é um domínio
                dom = self.conn.lookupByName(self.name)
                if not dom:
                    raise Exception(f"Domain {self.name} not found")

                memory_stats = dom.memoryStats()
                max_memory = dom.maxMemory() * 1024  # Convertendo para bytes
                current_memory = memory_stats.get('rss', 0) * 1024  # Convertendo para bytes

                if max_memory == 0:
                    raise Exception("Max memory reported as zero, unable to calculate memory usage")

                memory_usage_percent = (current_memory / max_memory) * 100

                return {
                    'total': max_memory,
                    'used': current_memory,
                    'free': max_memory - current_memory,
                    'percent_used': round(memory_usage_percent, 2)
                }
            else:  # Calcula para o host
                total_memory = self.conn.getInfo()[1] * 1024 * 1024  # Total em bytes
                free_memory = self.conn.getFreeMemory()

                if total_memory == 0:
                    raise Exception("Total memory reported as zero, unable to calculate memory usage")

                used_memory = total_memory - free_memory
                memory_usage_percent = (used_memory / total_memory) * 100

                return {
                    'total': total_memory,
                    'used': used_memory,
                    'free': free_memory,
                    'percent_used': round(memory_usage_percent, 2)
                }
        except libvirt.libvirtError as e:
            print(f"Failed to retrieve memory stats: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error calculating memory usage: {e}", file=sys.stderr)
            sys.exit(3)

class Domain(Libvirt):
    def __init__(self, domain=None, uri='qemu:///system'):
        self.name = domain
        super(self.__class__, self).__init__(uri)
    
    def get_info(self):
        self.domain = self.conn.lookupByName(self.name)
        self.isactive = self.domain.isActive()
        self.uuid = self.domain.UUIDString()
        if self.isactive:
            self.vcpus = { 'current': len(self.domain.vcpus()[0]),
                           'max': self.domain.maxVcpus() }
            self.memory = { 'current': self.domain.memoryStats()['actual'] *1024,
                            'max': self.domain.maxMemory() *1024 }
        else:
            self.vcpus = { 'current': 0,
                           'max': 0 }
            self.memory = { 'current': 0,
                            'max': 0 }
        return self.domain

    def list(self, active=None):
        self.domainlist = []
        try:
            if active is None:
                self.domainlist = [  d.name() for d in self.conn.listAllDomains(0) ]
            else:
                self.domainlist = [  d.name() for d in self.conn.listAllDomains(0) if d.isActive() == active ]
        except:
            print("Could not fetch list of domains.", file=sys.stderr)
            sys.exit(3)
        
        self.domainlist.sort()
        return self.domainlist
    
    def get_domain_cpu_usage(self, interval=1):
        """
        Retorna o uso de CPU do domínio em porcentagem (0 a 100).
        """
        try:
            # Coleta inicial de estatísticas de CPU
            cpu_time_1 = self.domain.info()[4]  # Tempo total de CPU em nanossegundos
            num_vcpus = self.domain.info()[3]  # Número de vCPUs alocadas ao domínio

            if num_vcpus == 0:
                raise Exception("No vCPUs allocated to the domain, unable to calculate CPU usage")

            import time
            time.sleep(interval)  # Espera pelo intervalo definido

            # Coleta final de estatísticas de CPU
            cpu_time_2 = self.domain.info()[4]

            # Calcula o tempo total de CPU usado entre as coletas
            cpu_time_diff = cpu_time_2 - cpu_time_1

            # Calcula o uso de CPU em porcentagem
            cpu_usage = (cpu_time_diff / (interval * num_vcpus * 1e9)) * 100

            return round(cpu_usage, 2)

        except libvirt.libvirtError as e:
            print(f"Failed to retrieve CPU stats for domain {self.name}: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error calculating CPU usage for domain {self.name}: {e}", file=sys.stderr)
            sys.exit(3)
            
    def get_memory_usage(self):
        """
        Retorna o uso de memória do domínio em porcentagem (0 a 100).
        """
        try:
            # Obtém as estatísticas de memória do domínio
            memory_stats = self.domain.memoryStats()

            # Memória configurada (total) para o domínio
            actual_memory = memory_stats.get('actual', 0) * 1024  # Convertendo para bytes

            # Memória diretamente utilizável
            usable_memory = memory_stats.get('usable', 0) * 1024  # Convertendo para bytes

            if actual_memory == 0:
                raise Exception("Actual memory reported as zero, unable to calculate memory usage")

            # Calcula a memória usada
            used_memory = actual_memory - usable_memory

            # Calcula o uso de memória em porcentagem
            memory_usage_percent = (used_memory / actual_memory) * 100

            return round(memory_usage_percent, 2)
        except libvirt.libvirtError as e:
            print(f"Failed to retrieve memory stats: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error calculating memory usage: {e}", file=sys.stderr)
            sys.exit(3)


            

class Net(Libvirt):
    def __init__(self, net=None, uri='qemu:///system'):
        self.name = net
        super(self.__class__, self).__init__(uri)

    def get_info(self):
        self.net = self.conn.networkLookupByName(self.name)
        self.isactive = self.net.isActive()
        self.uuid = self.net.UUIDString()
        return self.net

    def list(self, active=None):
        self.netlist = []

        try:
            if active is None:
                self.netlist = [ n.name() for n in self.conn.listAllNetworks(0) ]
            else:
                self.netlist = [ n.name() for n in self.conn.listAllNetworks(0) if n.isActive() == active]

        except:
            print("Could not fetch list of networks.", file=sys.stderr)

        self.netlist.sort()
        return self.netlist

class Pool(Libvirt):
    def __init__(self, pool=None, uri='qemu:///system'):
        self.name = pool
        super(self.__class__, self).__init__(uri)
 
    def get_info(self):
        self.pool = self.conn.storagePoolLookupByName(self.name)
        self.size = { 'total': self.pool.info()[1],
                      'free': self.pool.info()[3],
                      'used': self.pool.info()[2]
                    }
        self.isactive = self.pool.isActive()
        self.uuid = self.pool.UUIDString()

    def list(self, active=None):
        self.poollist = []
        try:
            if active is None:
                self.poollist = [ p.name() for p in self.conn.listAllStoragePools(0) ]
            else:
                self.poollist = [ p.name() for p in self.conn.listAllStoragePools(0) if p.isActive() == active ]
        except:
            print("Could not fetch list of storage pools.", file=sys.stderr)
            sys.exit(3)

        self.poollist.sort()
        return self.poollist

def is_none(data, errormsg, rc):
    if data is None:
        print(errormsg, file=sys.stderr)
        sys.exit(rc)

def list_to_zbx(data, label):
    if not isinstance(data, (list,tuple)):
        return data

    r = dict(data=[])
    return { 'data': [ { label: e } for e in data ] }

def parse_args():
    valid_resource_types = ["pool", "net", "domain", "host"]
    pool_valid_actions = ['list', 'total', 'used', 'free', 'active', 'UUID', 'count_active', 'count_inactive']
    net_valid_actions = ['list', 'active', 'UUID', 'count_active', 'count_inactive']
    domain_valid_actions = ['list', 'active', 'UUID', 'vcpus_current', 'vcpus_max', 'memory_current', 'memory_max', 'memory_usage', 'cpu_usage', 'count_active', 'count_inactive']
    host_valid_actions = ["version", "type", "cpu_usage", "memory_usage"]

    parser = argparse.ArgumentParser(description='Return KVM information for Zabbix parsing')
    parser.add_argument('-U', '--uri', help="Connection URI", metavar='URI', type=str, default='qemu:///system')
    parser.add_argument('-R', '--resource', metavar='RESOURCE', dest='resource', help='Resource type to be queried', type=str, default=None)
    parser.add_argument('-A', '--action', metavar='ACTION', dest='action', help='The name of the action to be performed', type=str, default=None)
    parser.add_argument('-d', '--domain', metavar='DOMAIN', dest='domain', help='The name of the domain to be queried', type=str, default=None)
    parser.add_argument('-n', '--net', metavar='NET', dest='net', help='The name of the net to be queried', type=str, default=None)
    parser.add_argument('-p', '--pool', metavar='POOL', dest='pool', help='The name of the pool to be queried', type=str, default=None)
    
    args = parser.parse_args()
    if args.resource not in valid_resource_types:
        parser.error("The resource specified (%s) is not supported. Please select one of: %s." % (args.resource, ", ".join(valid_resource_types)))

    if args.resource == "pool":
        if args.action not in pool_valid_actions:
            parser.error("The specified storage pool action (%s) is not supported. Please select one of: %s." % (args.action, ", ".join(pool_valid_actions)))
    elif args.resource == "net":
        if args.action not in net_valid_actions:
            parser.error("The specified network action (%s) is not supported. Please select one of: %s." % (args.action,  ", ".join(net_valid_actions)))
    elif args.resource == "domain":
        if args.action not in domain_valid_actions:
            parser.error("The specified domain action (%s) is not supported. Please select one of: %s." % (args.action, ", ".join(domain_valid_actions)))
    elif args.resource == "host":
        if args.action not in host_valid_actions:
            parser.error("The specified host action (%s) is not supported. Please select one of: %s." % (args.action, ", ".join(host_valid_actions)))

    return args

if __name__ == "__main__":
    main()
