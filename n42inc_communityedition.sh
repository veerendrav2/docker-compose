#!/bin/bash
key=$1
compose_script="n42incdocker_compose.py"
echo "--- Download agent ---"
wget -q -O "$compose_script" 'https://raw.githubusercontent.com/N42Inc/docker-compose/master/n42incdocker_compose.py'
echo $key
chmod +x "$compose_script"
