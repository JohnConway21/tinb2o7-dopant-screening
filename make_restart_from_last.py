# Restart a relaxation that died: take the LAST "ATOMIC_POSITIONS (crystal)" block printed in OLD.out
# and write NEW.in = OLD.in with those positions and a new prefix. Nothing else changes.
# Usage: python3 make_restart_from_last.py OLD NEW
import re, sys
old, new = sys.argv[1], sys.argv[2]
inp = open(old + ".in").read()
out = open(old + ".out", errors="ignore").read()
nat = int(re.search(r"nat\s*=\s*(\d+)", inp).group(1))
blk = out[out.rfind("ATOMIC_POSITIONS (crystal)"):].splitlines()[1:nat + 1]
atoms = [l.split()[:4] for l in blk]
assert len(atoms) == nat and all(len(a) == 4 for a in atoms), "incomplete block"
labels_in = [l.split()[0] for l in inp.split("ATOMIC_POSITIONS crystal\n")[1].split("K_POINTS")[0].strip().splitlines()]
assert [a[0] for a in atoms] == labels_in, "species order differs"
inp = re.sub(r"ATOMIC_POSITIONS crystal\n.*?(?=K_POINTS)", "ATOMIC_POSITIONS crystal\n" + "".join(f"  {a[0]} {a[1]} {a[2]} {a[3]}\n" for a in atoms), inp, flags=re.S)
inp, n = re.subn(r"prefix = '(.*?)'", lambda m: f"prefix = '{new.replace('relax_', '')}'", inp)
assert n == 1
open(new + ".in", "w").write(inp)
print(f"wrote {new}.in from the last of {out.count('ATOMIC_POSITIONS (crystal)')} position blocks in {old}.out")
