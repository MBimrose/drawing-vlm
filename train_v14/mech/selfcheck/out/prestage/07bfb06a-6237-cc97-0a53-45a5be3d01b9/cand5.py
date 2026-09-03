from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
corner_radius = 2.0
pocket_width = 30.0
pocket_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 22.0
hole_diameter = 4.0

base = Box(plate_width, plate_height, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)

pocket = Box(pocket_width, pocket_height, plate_thickness)
base = base - pocket

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = sp.part
base = base - Pos(-slot_offset, 0, -plate_thickness/2) * slot_solid

hole = Cylinder(hole_diameter/2, plate_thickness)
base = base - hole

part = base
part.name = "plate_with_pocket_slot_hole"
export_step(part, "output.step")