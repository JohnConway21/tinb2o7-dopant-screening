import os
from mp_api.client import MPRester

API_KEY = os.environ.get("MP_API_KEY")
if not API_KEY:
    raise ValueError("Please set the MP_API_KEY environment variable with your Materials Project API key.")

with MPRester(API_KEY) as mpr:
    structure = mpr.get_structure_by_material_id("mp-1216971")

structure.to(filename="TiNb2O7.cif")
print("Saved TiNb2O7.cif with", len(structure), "atoms")
