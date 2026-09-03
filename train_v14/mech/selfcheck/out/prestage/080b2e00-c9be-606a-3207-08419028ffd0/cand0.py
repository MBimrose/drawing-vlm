from build123d import *

plate_width = 60.0
plate_depth = 45.0
plate_thickness = 5.0
corner_fillet_radius = 4.0
slot_width = 30.0
slot_height = 10.0
slot_offset_y = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = -10.0
rib_thickness = 3.0
rib_height = 12.0
rib_offset = 2.0
chamfer_size = 0.8

base = Box(plate_width, plate_depth, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = chamfer(top_face.edges(), chamfer_size)

slot = Pos(0, slot_offset_y, 0) * Box(slot_width, slot_height, plate_thickness * 2)
base = base - slot

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib1 = Pos(-plate_width/2 + rib_offset + rib_thickness/2, 0, 0) * Box(rib_thickness, plate_depth - 2*rib_offset, rib_height)
rib2 = Pos(plate_width/2 - rib_offset - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_depth - 2*rib_offset, rib_height)

part = base + rib1 + rib2
part.name = "plate_with_ribs"
export_step(part, "output.step")