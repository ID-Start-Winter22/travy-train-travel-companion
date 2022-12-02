#!/bin/sh

# INSTALL APACHE, TOOLS
sudo apt update -y
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    apache2 \
    screen

# SET APACHE SOURCE DIR
#SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#sudo sh -c "cat >> /etc/apache2/apache2.conf << 'EOL'
#<Directory ${SCRIPT_DIR}>
#        Options Indexes FollowSymLinks
#        AllowOverride None
#        Require all granted
#        Allow from all
#</Directory>
#EOL"

# COPY WEB-STUFF TO APACHE2 DEFAULT DIR
IP=$1
if [ -z "$IP" ]
then 
  echo "IP param is unset! Aborting..."
  exit
else 
  echo "IP is set to '$1'"
fi

DIR=static
if [ -d "$DIR" ];
then # updated frontend is in use
    echo "$DIR directory exists. Replace localhost with $IP in constants.js..."
    sed -i -e "s/localhost/$IP/g" static/js/constants.js
    sudo cp -r $DIR /var/www/html
else # default frontend is in use
    echo "$DIR directory does not exist. Replace localhost with $IP in index.html..."
    sed -i -e "s/localhost/$IP/g" index.html
fi
sudo cp index.html /var/www/html
sudo systemctl restart apache2



# DOWNLOAD AND INSTALL MINICONDA
echo "------------------------------------"
echo "Downloading and installing Miniconda"
echo "------------------------------------"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
echo "____"
echo "DONE"
echo "____"

conda init

# CREATE RASAENV AND INSTALL RASA
echo "---------------------------------------"
echo "Creating virtual environment for Rasa"
echo "---------------------------------------"
conda create -n rasaenv python=3.9
conda activate rasaenv
echo "----"
echo "DONE"
echo "----"

echo " "

echo "---------------"
echo "Installing Rasa"
echo "---------------"
pip install rasa --no-cache-dir
echo "----"
echo "DONE"
echo "----"
