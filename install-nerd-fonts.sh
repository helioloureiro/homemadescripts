#! /bin/bash
#
#
## fish
#for font in (curl -s https://www.nerdfonts.com/font-downloads | grep zip | sd ".*href=\"" "" | sd "\".*" "" | sort -u)
#      curl -LO $font
#      set file (basename $font)
#      unzip -o $file
#      rm -f $file
#  end

mkdir -p .local/share/fonts  
cd .local/share/fonts

for zip in $(curl -s https://www.nerdfonts.com/font-downloads | grep zip | sed "s/.*href=\"//;s/\".*//" | sort -u)
do
    echo "Downloading: $zip"
    curl -LO $zip
    font=$(basename $zip)
    unzip -o $font
    rm -f $font
done

rm -f *.md

fc-cache -fv
