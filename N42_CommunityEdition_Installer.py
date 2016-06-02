'''
Author: Networks42
Description: Installs/Removes the N42 CE containers in Swarm Cluster
'''
import subprocess, re, sys, os
master_images="n42inc/n42ce_master:latest"
slave_image="n42inc/n42ce_slave:latest"
d = dict()
slaves=True
base_path=os.path.dirname(os.path.abspath(__file__))

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
        print output.strip(),"**Already installed docker-compose, nothing do to!..."
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

def install_n42Containers():
    try:
        key= sys.argv[1]
    except:
        print "Please Specify the KEY that you got from N42."
        print "Usage: python N42_CE_Installer.py <KEY> \n"
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
    
    with open('docker-compose-slaves.yml', 'w') as outfile:
        outfile.write( yaml.dump(compose_dict, default_flow_style=False) )
    with open('docker-compose-master.yml', 'w') as outfile:
        outfile.write( yaml.dump(master, default_flow_style=False) )

    print "***** Launching N42 Containers in the cluster *****\n"
    execute_cmd("docker-compose -f docker-compose-master.yml up -d")
    if slaves:
        execute_cmd("docker-compose -H :4000 -f docker-compose-slaves.yml up -d")
    os.remove("docker-compose-slaves.yml")
    os.remove("docker-compose-master.yml")
    print "Done!"


def remove_n42Container():
    slaves_con=""
    master_con=""
    try:
        containers_list=execute_cmd("docker -H :4000 ps -a")
        con_list_master=execute_cmd("docker ps -a")
        for line in containers_list.split("\n"):
            if line and re.search(slave_image,line):
                slaves_con=slaves_con+" "+line.split()[0]

        for master_line in con_list_master.split("\n"):
            if master_line and re.search(master_images,master_line):
                master_con=master_con+" "+master_line.split()[0]
        if master_con:
            print "Removing Master Container..."
            execute_cmd("docker stop "+master_con)
            execute_cmd("docker rm "+master_con)
        if slaves_con:
            print "Removing Slave Containers..."
            execute_cmd("docker -H :4000 stop "+slaves_con)
            execute_cmd("docker -H :4000 rm "+slaves_con)
        print "Done!"
    except:
        print "Some went wrong!, Docker Swarm containers are running?"

if __name__ == '__main__':
    while True:
        print "Please choose an option (1) or (2)"
        print "1.Install N42 Containers \n2.Remove N42 Containers"
        response = raw_input("Enter> ")
        if response == "1":
            install_n42Containers()
            break
        elif response == "2":
            remove_n42Container()
            break
        else:
            print "INVALID OPTION. Try Again!\n"
