#!/bin/bash
for f in $(echo *.txt); do
	echo $f
	echo ""
    cat $f | pcre2grep -Mo '([a,A][r,R][t,T]\b\.? *\d*.*\n?.*[u,U][s,S][t,T]\b *\d*)' >tmp
	cat tmp
	echo ""
	echo "end of $f"
	echo "$newyear $newpoz"
done >output
