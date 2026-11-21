#!/bin/zsh
# Run several pw.x jobs one after another inside ONE launchd job (survives Claude/terminal closing).
# Usage: ./run_chain_launchd.sh LABEL NAME1 NAME2 ...
# For each NAME: skip if NAME.out already ends with JOB DONE and passed its check; stop the chain if
# NAME.out exists unfinished (needs a manual restart), or if a finished run fails its check:
#   scf  -> must contain "convergence has been achieved"; relax -> must contain "bfgs converged".
# Never deletes or overwrites output. Log: chain_LABEL.log
set -e
REPO=/Users/devb/isef_project/stage1_validation; ENV=/Users/devb/miniforge3/envs/isef
label=$1; shift; names=("$@"); cd $REPO
if [[ $label != __inner ]]; then
  if pgrep -x pw.x >/dev/null; then echo "pw.x already running; not starting"; exit 1; fi
  for n in $names; do [[ -f $n.in ]] || { echo "missing $n.in"; exit 1; }; done
  plist=${TMPDIR:-/tmp}/isef.chain.$label.plist
  args=""; for n in __inner $label $names; do args+="<string>$n</string>"; done
  cat > $plist <<P
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>isef.chain.$label</string>
  <key>ProgramArguments</key><array><string>/usr/bin/caffeinate</string><string>-i</string><string>/bin/zsh</string><string>$REPO/run_chain_launchd.sh</string>$args</array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><false/>
  <key>WorkingDirectory</key><string>$REPO</string>
</dict></plist>
P
  launchctl bootout gui/$(id -u)/isef.chain.$label 2>/dev/null || true
  launchctl bootstrap gui/$(id -u) $plist; echo "started chain isef.chain.$label: $names"; exit 0
fi
label=$1; shift; names=("$@"); LOG=$REPO/chain_$label.log
export PATH=$ENV/bin:/usr/bin:/bin:/usr/sbin:/sbin OMP_NUM_THREADS=2
check() { local n=$1
  grep -q "JOB DONE" $n.out || return 1
  if grep -q "calculation = 'relax'" $n.in; then grep -q "bfgs converged" $n.out; else grep -q "convergence has been achieved" $n.out; fi
}
for n in $names; do
  if [[ -e $n.out ]]; then
    if check $n; then echo "$(date) skip $n (already done)" >> $LOG; continue
    else echo "$(date) STOP: $n.out exists but is unfinished or failed its check" >> $LOG; exit 1; fi
  fi
  echo "$(date) start $n" >> $LOG
  mpirun -np 3 pw.x < $n.in > $n.out 2>&1 || true
  if check $n; then echo "$(date) done $n: $(grep '^!' $n.out | tail -1)" >> $LOG
  else echo "$(date) STOP: $n failed its check" >> $LOG; exit 1; fi
done
echo "$(date) CHAIN COMPLETE" >> $LOG
