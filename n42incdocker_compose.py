import yaml
import subprocess,re,sys
def dockerinfo(port=4000):
  nodes = []
  info = subprocess.check_output(['docker', '-H',':4000','info'],shell=False).split('\n');
  for line in info:
    if re.search('2375', line) or re.search('4243', line):
       nodes.append(line.split(":")[0].strip())
  return nodes

nodes = dockerinfo(4000)
d = {}
key= sys.argv[1]
print "key:",key
for i in nodes:
    d[i] = {'network_mode':'host','privileged':True,'environment':['constraint:node=='+i,'key='+key],'image':'n42inc/n42ce_slave:latest','volumes':['/:/n42/','/sys/fs/cgroup/:/sys/fs/cgroup/','/var/lib/docker/:/var/lib/docker']}

compose_dict = {'version':'2','services':d}
#print compose_dict

with open('docker-compose-slaves.yml', 'w') as outfile:
    outfile.write( yaml.dump(compose_dict, default_flow_style=False) )


master = {'version':'2','services':{'master':{'image':'n42inc/n42ce_master:latest','network_mode':'host','environment':['key='+key]}}}

#print master

with open('docker-compose-master.yml', 'w') as outfile:
    outfile.write( yaml.dump(master, default_flow_style=False) )


print "it's create in current directory 2 docker-compose yml files \n 1.docker-compose-master.yml   run: docker-compose -f docker-compose-master.yml up -d \n 2.docker-compose-slaves.yml  run: docker-compose -H :4000 -f docker-compose-slaves.yml up -d  "
