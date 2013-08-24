import psutil
import time
import syslog
import re
import subprocess
import yaml
import sys


class MemoryMonitor(object):
    def __init__(self, configfile = "memory_monitor.yaml"):
        try:
            config = yaml.load(open(configfile))
        except IOError:
            print "Configuration file not found, not starting"
            sys.exit(-1)
        self.sleeptime = config['sleep-time']
        self.names = config['process-names']
        self.names_to_pid = {}

    def resolve_names(self):
        self.names_to_pid.clear()
        for process in psutil.process_iter():
            for pattern in self.names:
                matchObj = re.match(pattern, process.name)
                if (matchObj):
                    if process.name in self.names_to_pid:
                        if process.pid not in self.names_to_pid[process.name]:
                            self.names_to_pid[process.name].append(process.pid)
                    else:
                        self.names_to_pid[process.name] = [process.pid]

    def write_to_file(self, name, timestamp):
        for p in self.names_to_pid[name]:
            try:
                proc = psutil.Process(p)
                meminfo = proc.get_memory_info()
                pid = str(proc.pid)
                rms = str(meminfo[0])
                vms = str(meminfo[1])
            except psutil.NoSuchProcess:
                pid = "-1"
                rms = "-1"
                vms = "-1"
            toWrite = ",".join([
                        timestamp,
                        name,
                        pid,
                        rms,
                        vms,
                        "\n"
            ])
            syslog.syslog(toWrite)

    def write_command_output(self, commandDescr, output, timestamp):
        toWrite = " ".join([
                        timestamp,
                        commandDescr,
                        output,
                        "\n"
            ])
        syslog.syslog(toWrite)


    def dump_disk_usage_at(self, path, timestamp):
        output = subprocess.check_output(['/usr/bin/du', '-sh', path])
        output = output.replace("\t", " ").replace("\n", "")
        self.write_command_output("Disk usage ", output, timestamp)

    def dump_memory_usage(self, timestamp):
        mem = psutil.phymem_usage()
        output = "Total: %s, Used: %s, Free: %s" % (mem.total, mem.used, mem.free)
        self.write_command_output("Memory usage", output, timestamp)


if __name__ == "__main__":

    mm = MemoryMonitor()

    mm.resolve_names()

    syslog.syslog("# CSV format: time,name,pid,residentMemory,virtualMemory")
    while True:
        timeString = time.strftime("%b %d %H:%M:%S")
        for name in mm.names_to_pid.keys():
            mm.write_to_file(name, timeString)
        mm.dump_disk_usage_at('/tmp/', timeString)
        mm.dump_memory_usage(timeString)
        time.sleep(mm.sleeptime)
        mm.resolve_names()

