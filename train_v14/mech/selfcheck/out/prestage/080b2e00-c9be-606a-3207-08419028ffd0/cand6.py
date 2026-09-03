from build123d import *

plate_width = 60.0
plate_depth = 45.0
plate_thickness = 5.0
corner_radius = 4.0
slot_length = 30.0
slot_width = 10.0
slot_offset_y = 15.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = 15.0
chamfer_size = 0.8
rib_width = 10.0
rib_depth = 5.0
rib_height = 2.0

base = Box(plate_width, plate_depth, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = chamfer(top_face.edges(), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, rib_depth, rib_height)
base = base + rib

slot = Pos(0, slot_offset_y - plate_depth/2, 0) * Box(slot_length, slot_width, plate_thickness)
base = base - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, hole_offset_y - plate_depth/2, 0) * Cylinder(hole_diameter/2, plate_thickness)
    base = base - hole

part = base
part.name = "plate_with_rib_slot_holes"
export_step(part, "output.step")