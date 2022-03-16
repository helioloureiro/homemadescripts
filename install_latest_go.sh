#! /bin/bash

DESTDIR="/usr/local"  # where your go installation lives on

# curl -sL https://go.dev/dl/  | grep linux-amd64.tar.gz | head | sed "s/.*href=\"//;s/\">.*//" | grep "^/" | head -1

if [ $(id -u) -ne 0 ]; then
    echo "Run this script as root."
    exit 1
fi

SITE="https://go.dev"
TEMPDIR=$(mktemp -d)


latest=$(curl -sL $SITE/dl/ | \
    grep linux-amd64.tar.gz | \
    head | \
    sed "s/.*href=\"//;s/\">.*//" | \
    grep "^/" | \
    head -1)
go_release=$(basename $latest)
echo "Installing $go_release"

cd $TEMPDIR

curl -sLO "$SITE$latest"
tar zvf "$go_release"

version=$(echo $go_release | sed "s/linux.*//;s/^go//;s/\.\$//")

mv go go-$version
#ls -al

GO_INSTALLED_FLAG=0
which go >  /dev/null
if [ $? -eq 0 ]; then
    echo "Previous Go version:"$(go version)
    GO_INSTALLED_FLAG=1
fi

cd $DESTDIR
rm -f go
tar cf - -C $TEMPDIR go-$version | tar xf -
ln -s go-$version go
echo "Latest Go version:"$(go version)

if [ $GO_INSTALLED_FLAG -eq 0 ]; then
    if [ ! -d "$DESTDIR/bin" ]; then
        mkdir $DESTDIR/bin
    fi
    cd $DESTDIR/bin
    ln -s ../go/bin/* .
fi

rm -rf "$TEMPDIR"
