#!/bin/zsh
# Run one pw.x job through launchd so it does not depend on the terminal or the Claude app.
# Usage (from anywhere):  ./run_pw_launchd.sh NAME     runs NAME.in -> NAME.out once, never restarts.
# Refuses to start if pw.x is already running or NAME.out already exists (never overwrites output).
set -e
REPO=/Users/devb/isef_project/stage1_validation
ENV=/Users/devb/miniforge3/envs/isef
name=$1
label=isef.pw.$name
cd $REPO
[[ -n $name && -f $name.in ]] || { echo "no input $name.in"; exit 1; }
if pgrep -x pw.x >/dev/null; then echo "pw.x already running; not starting"; exit 1; fi
[[ -e $name.out ]] && { echo "$name.out exists; rename it first"; exit 1; }
plist=${TMPDIR:-/tmp}/$label.plist
cat > $plist <<P
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array>
    <string>/bin/zsh</string><string>-c</string>
    <string>export PATH=$ENV/bin:/usr/bin:/bin:/usr/sbin:/sbin; export OMP_NUM_THREADS=2; cd $REPO; exec /usr/bin/caffeinate -i mpirun -np 3 pw.x &lt; $name.in &gt; $name.out 2&gt;&amp;1</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><false/>
  <key>WorkingDirectory</key><string>$REPO</string>
</dict></plist>
P
launchctl bootout gui/$(id -u)/$label 2>/dev/null || true
launchctl bootstrap gui/$(id -u) $plist
echo "started $label (plist $plist)"
