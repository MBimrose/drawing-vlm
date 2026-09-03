from build123d import *

rail_length = 80.0
rail_width = 20.0
rail_height = 10.0
groove_width = 12.0
groove_depth = 2.0
groove_length = 60.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 10.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Pos(0, 0, rail_height/2) * Box(rail_length, rail_width, rail_height)
base = chamfer(base.edges().filter_by(Axis.X), chamfer_size)

groove = Pos(0, 0, rail_height - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
base = base - groove

rib_count = int((rail_length - rib_spacing) // rib_spacing)
rib_positions = [(-rail_length/2 + rib_spacing/2 + i * rib_spacing) for i in range(rib_count)]
for x in rib_positions:
    rib = Pos(x, 0, rib_height/2) * Box(rib_thickness, rail_width, rib_height)
    base = base + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, rail_height/2) * Cylinder(hole_diameter/2, rail_height)
    base = base - hole

part = base
part.name = "rail_with_groove_ribs_holes"
export_step(part, "output.step")