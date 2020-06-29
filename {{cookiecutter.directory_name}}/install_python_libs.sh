#!/bin/bash

pkg_dir=$1
# echo ${PKG_DIR}
# echo $1

regex="/([a-z]+)-([a-z]+)"

rm layers/*.zip

for file in layers-requirements/requirements-*.txt
do
    echo "Working with file : ${file}"
    if [[ $file =~ $regex ]]
    then
        layer=${BASH_REMATCH[2]}

        while read line
        do
            IFS='==' read -ra library <<< $line
            echo "Installing : ${library[0]}"
            pip install $line -t ${pkg_dir}
            find layers -type d -name '__pycache__' -exec rm -rf {} +
            find layers -type d -name '*.dist-info' -exec rm -rf {} +
        done < ${file}

        cd layers
        zip -r9 ../layer-${layer}.zip .
        rm -rf *
        cd ../
    else
        echo "Problems with the regex and creating the layer name (sad face)"
    fi
done

mv layer-*.zip ./layers
