#! /bin/bash

DESTDIR="/usr/local"  # where your go installation lives on

# curl -sL https://go.dev/dl/  | grep linux-amd64.tar.gz | head | sed "s/.*href=\"//;s/\">.*//" | grep "^/" | head -1

if [ $(id -u) -ne 0 ]; then
    echo "Run this script as root."
    exit 1
fi

SITE="https://go.dev"
TEMPDIR=$(mktemp -d)
PLATFORM=""
case $(uname -s) in
    Darwin) PLATFORM="darwin" ;;
    Linux) PLATFORM="linux";;
    *) echo "Platform not supported"
        exit 1
esac

case $(uname -m) in
    # not sure what Apple Intel would answer here
    i386) PLATFORM="$PLATFORM-arm64";;
    x86_64) PLATFORM="$PLATFORM-amd64";;
    arm*) PLATFORM="$PLATFORM-arm64";;
    aarch64) PLATFORM="$PLATFORM-arm64";;
    *) echo "Platform not supported"
        exit 1
esac


latest=$(curl -sL $SITE/dl/ | \
    grep $PLATFORM.tar.gz | \
    head | \
    sed "s/.*href=\"//;s/\">.*//" | \
    grep "^/" | \
    head -1)
go_release=$(basename $latest)
echo "Installing $go_release"

cd $TEMPDIR

curl -sLO "$SITE$latest"
tar zxvf "$go_release"

version=$(echo $go_release | sed "s/$PLATFORM.*//;s/^go//;s/\.\$//")

mv go go-$version
#ls -al

GO_INSTALLED_FLAG=0
which go >  /dev/null
if [ $? -eq 0 ]; then
    GO_INSTALLED_FLAG=1
    GO_OLD_VERSION=$(go version | awk '{print $3}' | sed "s/go//")
    echo "Previous Go version:"$GO_OLD_VERSION
fi

cd $DESTDIR
test -d go && mv go go-$GO_OLD_VERSION
rm -f go
test -d go-$version && rm -rf go-$version
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
