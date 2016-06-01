import subprocess, re, sys, os.path
d = dict()
slaves=True

def execute_cmd(cmd):
	return subprocess.check_output(cmd,shell=True)

def install_yaml():
	if os.path.exists("/etc/redhat-release"):
		execute_cmd("yum install -y python-yaml")
	elif os.path.exists("/etc/debian_version"):
		execute_cmd("apt-get install -y python-yaml")

def install_docker_compose():
	try:
		output = execute_cmd("docker-compose -v")
		print output.strip(),"**Already Installed Docker-Compose..."
	except:
		print "Installing Docker-Compose..."
		try:
			execute_cmd("curl -L https://github.com/docker/compose/releases/download/1.7.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose")
			execute_cmd("chmod +x /usr/local/bin/docker-compose")
		except:
			print "Problem with installing docker-compose, please install manually"
			sys.exit()

def get_swarm_nodes():
	global slaves
	nodes = []
	try:
		info = execute_cmd("docker -H :4000 info").split('\n')
		for line in info:
			if re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line):
				nodes.append(line.split(":")[0].strip())
		if not nodes:
			print "There were no nodes in SWARM cluster except current node(Master). So, will launch only 'n42ce_master' but not 'n42ce_slave'"
			slaves=False
		else:
			slaves=True
		return nodes
	except:
  		print "Docker Swarm Installed? or Docker Swarm Containers are running? Please Check!"
  		sys.exit()

try:
	key= sys.argv[1]
except:
	print "Please Specify the KEY that you got from N42."
	print "Usage: python N42_CommunityEdition_Installer.py <KEY> \n"
	sys.exit()

install_yaml()
import yaml
install_docker_compose()
nodes = get_swarm_nodes()

print "The Given Key is",key
for i in nodes:
    d[i] = {'network_mode':'host','privileged':True,'environment':['constraint:node=='+i,'key='+key],'image':'n42inc/n42ce_slave:latest','volumes':['/:/n42/','/sys/fs/cgroup/:/sys/fs/cgroup/','/var/lib/docker/:/var/lib/docker']}

compose_dict = {'version':'2','services':d}
master = {'version':'2','services':{'master':{'image':'n42inc/n42ce_master:latest','network_mode':'host','environment':['key='+key]}}}

print "Generating yaml files..."
with open('docker-compose-slaves.yml', 'w') as outfile:
    outfile.write( yaml.dump(compose_dict, default_flow_style=False) )
with open('docker-compose-master.yml', 'w') as outfile:
    outfile.write( yaml.dump(master, default_flow_style=False) )


print "***** Launching N42 Containers in the cluster *****\n"
execute_cmd("docker-compose -f docker-compose-master.yml up -d")
if slaves:
	execute_cmd("docker-compose -H :4000 -f docker-compose-slaves.yml up -d")
print "Done!"
