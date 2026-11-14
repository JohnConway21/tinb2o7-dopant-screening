import re, sys

relax_out, template_in, new_in, new_prefix = sys.argv[1:5]

text = open(relax_out).read()
m = re.search(r"Begin final coordinates.*?ATOMIC_POSITIONS \(crystal\)\n(.*?)End final coordinates", text, re.S)
if not m:
    sys.exit("No final coordinates found; did the relaxation converge?")
final = [l.strip() for l in m.group(1).strip().split("\n") if l.strip()]
if len(final) != 30:
    sys.exit(f"Expected 30 atoms, found {len(final)}")

inp = open(template_in).read()
old = re.search(r"ATOMIC_POSITIONS crystal\n(.*?)K_POINTS", inp, re.S)
new_block = "ATOMIC_POSITIONS crystal\n" + "\n".join("  " + l for l in final) + "\n"
inp = inp.replace(old.group(0), new_block + "K_POINTS")
inp = re.sub(r"prefix = '.*?'", f"prefix = '{new_prefix}'", inp)
open(new_in, "w").write(inp)
print(f"Wrote {new_in} with {len(final)} relaxed atoms")
