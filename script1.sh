#!/bin/bash
for f in $(echo *.txt); do
	year=$(echo $f | awk -F "_" '{print $1}')
	poz=$(echo $f | awk -F "_" '{print $2}' | awk -F "." '{print $1}')
	newnum=$(cat $f | grep '[^\s]' | grep -m 1 . | pcre2grep -M '^ *Dz\.U\. *z *[0-9]{4} *r\. *Nr *\d*,? *poz')
	newyear=$(echo $newnum | awk -F " " '{print $3}')
	newpoz=$(echo $newnum | awk -F " " '{print $8}')
	echo $f
	echo ""
    cat $f | perl -pe "s/$newpoz(.*?)$newyear//" | perl -pe "s/$newyear(.*?)$newpoz//" | perl -pe "s/$poz(.*?)$year//" | perl -pe "s/$year(.*?)$poz//" | perl -pe 's/\n/ /' | pcre2grep -Mio '(\d{4}[ \.]? *r\b)(.*?)(poz[ \.\d] *\d* *\))' | pcre2grep -Mi '\bdz\b' > tmp
    cat $f | perl -pe "s/$newpoz(.*?)$newyear//" | perl -pe "s/$newyear(.*?)$newpoz//" | perl -pe "s/$poz(.*?)$year//" | perl -pe "s/$year(.*?)$poz//" | perl -pe 's/\n/ /'  > tmp2
    echo "" > out1/$f.out
    cat tmp |
        while read line; do
            cat tmp2 | sed 's|'"$line"'||g' > tmp3
            rm tmp2
            mv tmp3 tmp2
            echo $line
            line=$( echo $line | perl -pe 's/ +/ /g')
            echo -n "$(echo $line | pcre2grep -io '\d{4}(\.?) *r/b'). " >> out1/$f.out
            echo -n      "$(echo $line | pcre2grep -io '(?<=\d{4})(.*?)(?=\(Dz)' | sed 's/r\.? *//') " >> out1/$f.out
            echo -n "$(echo $line | pcre2grep -io '(?<=\(Dz)(.*?)(?=\d{4})' | perl -pe 's/(.*)r\.? */\1/') " >> out1/$f.out
            echo "$(echo $line | pcre2grep -io '\( *dz(.*?)\)') " >> out1/$f.out
            line=$(echo $line | perl -pe 's/poz//')
            while [[ $(echo $line | grep 'poz') ]]; do
                echo "" >> out1/$f.out #additional lines if there are more position (to count references)
                line=$(echo $line | sed 's/poz//')
            done
        done
        cat tmp2 | perl -pe 's/(\d{4}\.? *r)/<tmpatr>\1/g' | pcre2grep -Mio '((\d{4}[ \.]? *r\b)(.*?)(?=<tmpatr>))' |
        while read line; do
            if [[ $(echo $line | grep 'poz') ]]; then
                continue
            fi
            echo -n "$(echo $line | pcre2grep -io '\d{4}\.? *r/b'). " >> out1/$f.out
            echo -n "$(echo $line | pcre2grep -io '(?<=\d{4})(.*?)(?=\bpoz\b)' | sed 's/r\.? *//') " >> out1/$f.out
            echo -n "$(echo $line | pcre2grep -io '(?<=\bpoz\b)(.*?)(?=\d{4})' | perl -pe 's/(.*)r\.? */\1/') " >> out1/$f.out
            while [[ $(echo $line | grep 'poz') ]]; do
                echo "$(echo $line | pcre2grep -io '\dpoz[ \.\d] *\d*')" >> out/$f.out
                line=$(echo $line | sed 's/poz//')
            done
        done
	echo ""
	echo "end of $f"
	echo "$newyear $newpoz"
done
