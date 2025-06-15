#!/usr/bin/env bash
# wait-for-it.sh: Wait until a host and port are available

set -e

host="$1"
port="$2"
shift 2

until nc -z "$host" "$port"; do
  echo "Waiting for $host:$port..."
  sleep 1
done

exec "$@"
