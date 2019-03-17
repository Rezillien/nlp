#!/bin/bash
for f in $(echo *.txt); do
	year=$(echo $f | awk -F "_" '{print $1}')
	poz=$(echo $f | awk -F "_" '{print $2}' | awk -F "." '{print $1}')
	newnum=$(cat $f | grep '[^\s]' | grep -m 1 . | pcre2grep -M '^ *Dz\.U\. *z *[0-9]{4} *r\. *Nr *\d*,? *poz')
	newyear=$(echo $newnum | awk -F " " '{print $3}')
	newpoz=$(echo $newnum | awk -F " " '{print $8}')
	echo $f
	echo ""
	cat $f | pcre2grep --match-limit 10000000 --heap-limit 100000000 --depth-limit 100000000 -M '.*\n.*\n.*([0-9]{4} ?r(o|\b).*\n?.*[p,P][o.O][z,Z]\b|[p,P][o,O][z,Z]\b.*\n?.*[0-9]{4} ?r(o|\b)).*\n.*' | pcre2grep -M '^(?!((.*'"$year"' ?r.*\n?.*poz.*'"$poz"')|(.*'"$newyear"' ?r.*\n?.*poz.*'"$newpoz"'))).*$' >tmp
	cat tmp
	echo ""
	echo "end of $f"
	echo "$newyear $newpoz"
done >output
