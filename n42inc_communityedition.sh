#!/bin/bash
key=$1
compose_script="n42incdocker_compose.py"
echo "--- Download agent ---"
wget -q -O "$compose_script" 'https://raw.githubusercontent.com/N42Inc/docker-compose/master/n42incdocker_compose.py'
echo $key
chmod +x "$compose_script"
chmod +x n42inc_communityedition.sh

python "$compose_script" $key
docker-compose -f docker-compose-master.yml up -d
docker-compose -H :4000 -f docker-compose-slaves.yml up -d

