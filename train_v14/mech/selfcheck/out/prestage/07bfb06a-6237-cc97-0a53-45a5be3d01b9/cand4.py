from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_spacing = 12.0
num_slots = 3
fillet_radius = 2.0
rib_width = 8.0
rib_height = 30.0

base = Box(plate_width, plate_height, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
base = base - Box(cutout_width, cutout_height, plate_thickness)

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_tool = sp.part

for i in range(num_slots):
    x = -plate_width/2 + slot_spacing + i * slot_spacing
    base = base - Pos(x, 0, -plate_thickness/2) * slot_tool

rib = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
part = base + rib
part.name = "plate_with_cutout_slots_rib"
export_step(part, "output.step")