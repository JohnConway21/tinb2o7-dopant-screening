#!/bin/zsh
# Runs every minute via launchd (isef.batteryguard). If on battery power and charge < 5%,
# saves the newest relax_*.out: snapshot copy, last ATOMIC_POSITIONS -> *_last_positions.txt,
# a RESULTS-independent log line, then git commit + push. Fires once per discharge.
# Never stops pw.x and never deletes anything.
REPO=/Users/devb/isef_project/stage1_validation
FLAG=$REPO/.battery_guard_fired
LOG=$REPO/battery_guard.log
cd $REPO || exit 0
b=$(pmset -g batt)
pct=$(echo "$b" | grep -o '[0-9]*%' | head -1 | tr -d '%')
# A weak charger can show "AC attached; not charging" while the battery still drains (2026-11-25: 45 W
# adapter, resumed at 8% and kept draining). Count that as safe only when charge >= 30% (e.g. the macOS
# 80% charge hold); otherwise treat it like battery power: no auto-resume, clean stop at <=10%.
safe=1
echo "$b" | grep -q "Battery Power" && safe=0
echo "$b" | grep -q "not charging" && [[ -n $pct && $pct -lt 30 ]] && safe=0
if [[ $safe == 1 ]]; then
  rm -f $FLAG $FLAG.exit
  # On AC: auto-resume a pipeline step that was stopped cleanly by the low-battery EXIT request.
  last=$(tail -1 pipeline.log 2>/dev/null)
  if ! pgrep -x pw.x >/dev/null && [[ $last == *"STOP: "*" failed its check"* ]]; then
    x=$(echo "$last" | sed -E 's/.*STOP: ([^ ]+) failed.*/\1/')
    if [[ -f $x.out && ! -e $x.accepted ]] && grep -q "Program stopped by user request" $x.out; then
      base=$(echo $x | sed -E 's/_r[0-9]+$//'); k=2; while [[ -e ${base}_r$k.in ]]; do k=$((k+1)); done; new=${base}_r$k
      if grep -q "restart_mode" $x.in; then cp $x.in $new.in
      else sed -E "s/(calculation = '[a-z]+',)/\1\n  restart_mode = 'restart',/" $x.in > $new.in; fi
      pre=$(grep -o "prefix = '[^']*'" $new.in | cut -d"'" -f2); rm -f $REPO/$pre.EXIT $REPO/tmp/$pre.EXIT
      echo "$(date) on AC: auto-resuming $x as $new" >> $LOG
      $REPO/run_pipeline_launchd.sh >> $LOG 2>&1
    fi
  fi
  exit 0
fi
# At <=10%: ask the running pw.x to stop cleanly (prefix.EXIT). QE finishes its current SCF iteration,
# writes restart files (charge density, wavefunctions, BFGS history) and exits, so the in-progress step
# can be resumed with restart_mode='restart' instead of being lost. Done once per discharge.
if [[ -n $pct && $pct -le 10 && ! -e $FLAG.exit ]] && pgrep -x pw.x >/dev/null; then
  touch $FLAG.exit
  run=$(ls -t *.out | head -1); pre=$(grep -o "prefix = '[^']*'" ${run%.out}.in | cut -d"'" -f2)
  if [[ -n $pre ]]; then touch $REPO/$pre.EXIT $REPO/tmp/$pre.EXIT
    echo "$(date) battery ${pct}%: requested clean stop of $run (created $pre.EXIT)" >> $LOG; fi
fi
[[ -z $pct || $pct -ge 5 || -e $FLAG ]] && exit 0
touch $FLAG
out=$(ls -t relax_*.out 2>/dev/null | head -1)
ts=$(date +%Y%m%d_%H%M)
echo "$(date) battery ${pct}%: saving $out" >> $LOG
if [[ -n $out ]]; then
  base=${out%.out}
  cp $out $out.snapshot_$ts
  /usr/bin/python3 - "$out" "${base}_last_positions.txt" <<'PY' >> $LOG 2>&1
import sys
lines=open(sys.argv[1],errors='ignore').read().splitlines()
idx=[k for k,l in enumerate(lines) if l.startswith('ATOMIC_POSITIONS')]
if idx:
    i=idx[-1]; j=i+1
    while j<len(lines) and lines[j].strip() and not lines[j].startswith('End'): j+=1
    open(sys.argv[2],'w').write('\n'.join(lines[i:j])+'\n'); print('saved',j-i-1,'atoms to',sys.argv[2])
nrg=[l for l in lines if l.startswith('!')]; frc=[l for l in lines if 'Total force' in l]
print('last energy:', nrg[-1].strip() if nrg else None); print('last force:', frc[-1].strip() if frc else None)
PY
  /usr/bin/git add battery_guard.log ${base}_last_positions.txt 2>>$LOG
fi
/usr/bin/git add battery_guard.log
/usr/bin/git commit -qm "Auto-save at ${pct}% battery ($ts)" >> $LOG 2>&1
/usr/bin/git push -q >> $LOG 2>&1 && echo "pushed" >> $LOG || echo "push failed (commit is local)" >> $LOG
