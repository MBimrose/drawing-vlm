from build123d import *

outer_radius = 40.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 60.0
rib_thickness = 2.0
rib_height = 10.0
rib_count = 6
slot_width = 12.0
slot_depth = 2.0
fillet_radius = 1.0

result = Pos(0, 0, height/2) * (Cylinder(outer_radius, height) - Cylinder(inner_radius, height))

rib = Pos(inner_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

slot = Pos(outer_radius - slot_depth/2, 0, slot_depth/2) * Box(slot_width, height, slot_depth)
result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "XMountSocket"
export_step(part, "output.step")