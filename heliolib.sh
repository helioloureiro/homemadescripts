# source me

Black_FG=30
Black_BG=40
Red_FG=31
Red_BG=41
Green_FG=32
Green_BG=42
Brown_FG=33
Brown_BG=43
Blue_FG=44
Blue_BG=44
Purple_FG=35
Purple_BG=45
Cyan_FG=36
Cyan_BG=46
Gray_FG=37
Gray_BG=47

Normal=0
Bold=1
Underline=4
Blinking=5
Reverse=7
Reset="\e[0m"

getcolor() {
  color="$1"
  case $color in
    Black_FG) color_id=30;;
    Black_BG) color_id=40;;
    Red_fG) color_id=31;;
    Red_BG) color_id=41;;
    Green_FG) color_id=32;;
    Green_BG) color_id=42;;
    *) color_id=0;;
  esac
  echo -en "\e[${color_id}m"
}

resetcolor() {
  echo -en "$Reset"
}

die() {
  echo -en "$(getcolor Red_FG)ERROR:$(resetcolor) "
  echo "$*" >&2 
  exit 1
}

printbar() {
  local sizeof="$1"
  while [ $sizeof -gt 0 ]
  do
    echo -n "-"
    sizeof=$((sizeof-1))
  done
}

repeat_char() {
  local c="$1"
  local counter="$2"
  while [ $counter -gt 0 ]
  do
    echo -n "$c"
    counter=$((counter-1))
  done

}

printbox() {
  msg="$*"
  sizeof=$(echo -n "$msg" | wc -c)
  # add one space at the beginning and other at the end
  sizeof=$((sizeof+2))
  echo -n "┌"
  repeat_char "─" $sizeof 
  echo "┐"

  echo -n "│"
  repeat_char " " $sizeof
  echo "│"

  echo "│ $msg │"

  echo -n "│"
  repeat_char " " $sizeof
  echo "│"

  echo -n "└"
  repeat_char "─" $sizeof 
  echo "┘"
}

if [ "$0" == "$BASH_SOURCE" ]; then
  die "heliolib.sh is supposed to be sourced"
fi
