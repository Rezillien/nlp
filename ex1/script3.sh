#!/bin/bash
for f in $(echo *.txt); do
	echo -n $f" "
    cat $f | pcre2grep -oiu '\bustaw(a|y|ie|ę|ą|ie|o|om|ami|ach)?\b'
done > tmp
cat tmp | sort -rn -k2 | wc -l > output3 
rm tmp

