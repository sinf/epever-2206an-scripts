#!/bin/sh

[ -f .env ] && . ./.env
[ -z "$server" ] && export server=http://127.0.0.1:8000

function sync_one_value() (
  set +ex
  key=$1
  expect="$2"
  prefix="$(date +%Y-%m-%dT%H:%M:%S%z) $key"
  echo "$prefix expect=$expect"
  if ! reported="$(curl -sf $server/$key -o - | sed -n 's/^ *"value": \(.*\),$/\1/p')"
  then
    echo "$prefix read error"
    exit 1
  fi
  echo "$prefix reported=$reported"
  if [ ! x"$expect" = x"$reported" ]; then
    if curl -sf $server/$key -d "$expect" >/dev/null
    then
      echo "$prefix write success"
    else
      echo "$prefix write error"
      exit 1
    fi
    if ! reported="$(curl -sf $server/$key -o - | sed -n 's/^ *"value": \(.*\),$/\1/p')"
    then
      echo "$prefix read error"
      exit 1
    fi
    if [ ! x"$expect" = x"$reported" ]; then
      echo "$prefix write success but reported still wrong"
      exit 1
    fi
  fi
)

#echo "$0: server=$server config_dir=$config_dir"
#cd "$config_dir"
#set -e
#for filename in $(find . -type f | sort -n); do
#  key="$(basename $filename | sed 's/^[0-9]\+[-._]\?//')"
#  sync_one_value $filename $key
#done
#
