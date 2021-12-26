#!/bin/bash

# if folder does not exit create it
mkdir -p $1

# download datasets
kaggle datasets download mylesoneill/world-university-rankings -p $1 --unzip -o &&
# check if the donwloaded dataset is the same as the tracked one by git
# or it is not tracked yet
#git ls-files -t -o -m $1 | grep $1


git add $1
git commit -m "Exp2: Added raw data from kaggle" 1>/dev/null

exit 0

