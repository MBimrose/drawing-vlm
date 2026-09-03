from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
edge_fillet_radius = 2.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 10.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), edge_fillet_radius)

cutout = Box(cutout_width, cutout_height, plate_thickness)
base = base - cutout

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = sp.part

slot_x = -plate_length/2 + slot_offset
base = base - Pos(slot_x, 0, -plate_thickness/2) * slot_solid

part = base
part.name = "plate_with_cutout_and_slot"
export_step(part, "output.step")