from build123d import *

leg_length = 50.0
leg_width = 30.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 5.0
countersink_diameter = 9.0
countersink_angle = 82.0
countersink_depth = 2.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 10.0
rib_offset = 5.0

vertical = Pos(0, 0, thickness/2) * Box(leg_length, leg_width, thickness)
horizontal = Pos(leg_length - leg_width, leg_width, thickness/2) * Box(leg_width, leg_length, thickness)
base = vertical + horizontal

edges = base.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
base = fillet(edges, fillet_radius)

hole_center_x = leg_length - leg_width / 2.0
hole_center_y = leg_length
shaft = Pos(hole_center_x, hole_center_y, thickness/2) * Cylinder(hole_diameter/2, thickness)
csink = Pos(hole_center_x, hole_center_y, thickness - countersink_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, countersink_depth)
base = base - shaft - csink

rib_count = int((leg_length - 2 * rib_offset) // rib_spacing)
for i in range(rib_count):
    x = -leg_length/2 + rib_offset + i * rib_spacing
    rib = Pos(x, -leg_width/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    base = base + rib

part = base
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")