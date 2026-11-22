#!/bin/zsh
# Start pipeline_relaxed_ref.py as one launchd job (survives Claude closing). Re-running resumes:
# finished steps are skipped; an unfinished step stops the pipeline (restart it by hand first).
REPO=/Users/devb/isef_project/stage1_validation; ENV=/Users/devb/miniforge3/envs/isef; label=isef.pipeline
pgrep -x pw.x >/dev/null && { echo "pw.x already running; not starting"; exit 1; }
plist=${TMPDIR:-/tmp}/$label.plist
cat > $plist <<P
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>/bin/zsh</string><string>-c</string>
  <string>export PATH=$ENV/bin:/usr/bin:/bin:/usr/sbin:/sbin; export OMP_NUM_THREADS=2; cd $REPO; exec /usr/bin/caffeinate -i $ENV/bin/python pipeline_relaxed_ref.py</string></array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><false/>
  <key>WorkingDirectory</key><string>$REPO</string>
</dict></plist>
P
launchctl bootout gui/$(id -u)/$label 2>/dev/null || true
launchctl bootstrap gui/$(id -u) $plist && echo "started $label"
