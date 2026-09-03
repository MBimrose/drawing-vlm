from build123d import *

width = 80.0
depth = 60.0
thickness = 5.0
corner_radius = 6.0
edge_chamfer = 0.7
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 10.0
rib_count = 4
hole_diameter = 3.0
cbore_diameter = 5.0
cbore_depth = 2.0
hole_offset_x = 20.0
hole_offset_y = 20.0

base = Pos(-width/2, -depth/2, thickness/2) * Box(width, depth, thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = chamfer(top_face.edges(), edge_chamfer)

for i in range(rib_count):
    y_pos = -depth/2 + rib_spacing * (i - (rib_count - 1) / 2)
    rib = Pos(rib_thickness/2, y_pos, thickness/2) * Box(rib_thickness, rib_thickness, rib_height)
    base = base + rib

shaft = Pos(hole_offset_x, hole_offset_y, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)
cbore = Pos(hole_offset_x, hole_offset_y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
base = base - shaft - cbore

part = base
part.name = "XMountSocket"
export_step(part, "output.step")