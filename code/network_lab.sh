#!/usr/bin/env bash
# Isolated, static, dual-stack network. Run inside an Ubuntu VM.
set -euo pipefail
names=(iot-sensor iot-router iot-cloud)
if [[ $EUID -ne 0 ]]; then
  echo "Run: sudo bash network_lab.sh up|down" >&2
  exit 1
fi
exists() { ip netns list | awk '{print $1}' | grep -qx "$1"; }
remove_lab() {
  for ns in "${names[@]}"; do
    if exists "$ns"; then ip netns del "$ns"; fi
  done
}
case "${1:-}" in
  down)
    for ns in "${names[@]}"; do
      if exists "$ns" && [[ -n $(ip netns pids "$ns") ]]; then
        echo "Stop processes in $ns before cleanup." >&2
        exit 1
      fi
    done
    remove_lab
    exit 0
    ;;
  up) ;;
  *) echo "Usage: sudo bash network_lab.sh up|down"; exit 1 ;;
esac
for ns in "${names[@]}"; do
  if exists "$ns"; then
    echo "$ns already exists; clean up the previous lab first." >&2
    exit 1
  fi
done
trap remove_lab ERR
for ns in "${names[@]}"; do
  ip netns add "$ns"
  ip -n "$ns" link set lo up
done
ip -n iot-sensor link add s0 type veth peer name r0 netns iot-router
ip -n iot-router link add r1 type veth peer name c0 netns iot-cloud
ip -n iot-sensor addr add 10.10.1.2/24 dev s0
ip -n iot-router addr add 10.10.1.1/24 dev r0
ip -n iot-router addr add 10.10.2.1/24 dev r1
ip -n iot-cloud addr add 10.10.2.2/24 dev c0
ip -n iot-sensor -6 addr add 2001:db8:1::2/64 dev s0 nodad
ip -n iot-router -6 addr add 2001:db8:1::1/64 dev r0 nodad
ip -n iot-router -6 addr add 2001:db8:2::1/64 dev r1 nodad
ip -n iot-cloud -6 addr add 2001:db8:2::2/64 dev c0 nodad
ip -n iot-sensor link set s0 up
ip -n iot-router link set r0 up
ip -n iot-router link set r1 up
ip -n iot-cloud link set c0 up
ip netns exec iot-router sysctl -qw net.ipv4.ip_forward=1
ip netns exec iot-router sysctl -qw net.ipv6.conf.all.forwarding=1
ip -n iot-sensor route add 10.10.2.0/24 via 10.10.1.1
ip -n iot-cloud route add 10.10.1.0/24 via 10.10.2.1
ip -n iot-sensor -6 route add 2001:db8:2::/64 via 2001:db8:1::1
ip -n iot-cloud -6 route add 2001:db8:1::/64 via 2001:db8:2::1
trap - ERR
echo "READY: iot-sensor <-> iot-router <-> iot-cloud"
