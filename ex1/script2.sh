#!/bin/bash
for f in $(echo *.txt); do
	echo $f
	echo ""
    cat $f | perl -pe 's/^ *[Aa][rR][tT]\.? *\d*\.? *$/<tmp2atr>/g' | perl -pe 's/\b[aA][rR][tT]\b/<tmpatr>art/g' | perl -pe 's/\n/ /g' | pcre2grep -Moi '\bart[ \.\d] *\d+(.*?)(?=<tmpatr>)' >tmp
    echo "" > out2/$f.out
    cat tmp | pcre2grep -oMi 'art(.*?)ust[\. \d] *\d*' |
        while read line; do
            while [[ $(echo $line | grep 'ust') ]]; do
                ust=$(echo $line | pcre2grep -oMi 'ust[ \.\d] *\d+' | tail -n-1)
                if [[ $(echo $line | pcre2grep  '<tmp2atr>') ]]; then
                    echo $(echo $line | pcre2grep -oMi 'ust[ \.\d] *\d+' | tail -n-1) >> out2/$f.out
                else
                    echo -n "$(echo $line | pcre2grep -oMi 'art[ \.\d] *\d+') " >> out2/$f.out
                    echo $(echo $line | pcre2grep -oMi 'ust[ \.\d] *\d+' | tail -n-1) >> out2/$f.out
                fi
                line=$(echo $line | perl -pe "s/$ust.*$//")
            done
        done
    cat $f | perl -pe 's/^ *[Aa][rR][tT]\.? *\d*\.? *$/<tmp2atr>/g' | perl -pe 's/\b[aA][rR][tT]\b/<tmpatr>art/g' | perl -pe 's/\n/ /g' | perl -pe 's/\bart[ \.\d] *\d+(.*?)(?=<tmpatr>)//g' >tmp
    cat tmp |
        while read line; do
            while [[ $(echo $line | grep 'ust') ]]; do
                ust=$(echo $line | pcre2grep -oMi 'ust[ \.\d] *\d+' | tail -n-1)
                echo $(echo $line | pcre2grep -oMi 'ust[ \.\d] *\d+' | tail -n-1) >> out2/$f.out
                line=$(echo $line | perl -pe "s/$ust.*$//")
            done
        done
done
