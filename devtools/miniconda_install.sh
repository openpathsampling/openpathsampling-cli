#!/bin/bash

### Install Miniconda

if [ -z "$CONDA_PY" ]
then
    CONDA_PY=3.8
fi

if [ -z "$OS_ARCH" ]
then
    OS_ARCH=Linux-x86_64
fi

# universal MD5 checker
MD5_CMD=`basename $(command -v md5sum || command -v md5 || command -v openssl)`
declare -A opts=( ["md5"]="-r" ["openssl"]="md5 -r" ["md5sum"]="" )
MD5_OPT=" ${opts[$MD5_CMD]}"

pyV=${CONDA_PY:0:1}
conda_version="latest"
#conda_version="4.4.10"  # can pin a miniconda version like this, if needed

MINICONDA=Miniconda${pyV}-${conda_version}-${OS_ARCH}.sh
MINICONDA_MD5=$(curl -sL https://repo.continuum.io/miniconda/ | grep -A3 $MINICONDA | sed -n '4p' | sed -n 's/ *<td>\(.*\)<\/td> */\1/p')
wget https://repo.continuum.io/miniconda/$MINICONDA
SCRIPT_MD5=`eval "$MD5_CMD $MD5_OPT $MINICONDA" | cut -d ' ' -f 1`

if [[ $MINICONDA_MD5 != $SCRIPT_MD5 ]]; then
    echo "Miniconda MD5 mismatch"
    echo "Expected: $MINICONDA_MD5"
    echo "Found: $SCRIPT_MD5"
    exit 1
fi
bash $MINICONDA -b -p $HOME/miniconda${pyV}

conda init bash
source ~/.bashrc

export PATH=$HOME/miniconda${pyV}/bin:$PATH

conda update --yes conda
rm -f $MINICONDA
