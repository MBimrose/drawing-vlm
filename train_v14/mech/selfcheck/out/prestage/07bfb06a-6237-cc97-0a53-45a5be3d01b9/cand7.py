from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 10.0
fillet_radius = 2.0

base = Box(plate_width, plate_height, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

cutout = Box(cutout_width, cutout_height, plate_thickness)
base = base - cutout

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = sp.part

slot1 = Pos(-plate_width/2 + slot_offset, 0, -plate_thickness/2) * slot_solid
slot2 = Pos(-plate_width/2 + slot_offset + slot_length, 0, -plate_thickness/2) * slot_solid
base = base - slot1 - slot2

part = base
part.name = "plate_with_cutouts"
export_step(part, "output.step")