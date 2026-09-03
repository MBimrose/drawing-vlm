from build123d import *

base_length = 80.0
base_width = 30.0
base_thickness = 10.0
rib_width = 20.0
rib_height = 5.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 3.3
hole_spacing_x = 40.0
hole_spacing_y = 24.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
rib = Pos(0, 0, rib_height/2) * Box(rib_width, base_width, rib_height)
combined = base + rib

top_face = combined.faces().sort_by(Axis.Z)[-1]
combined = fillet(top_face.edges(), fillet_radius)

bottom_face = combined.faces().sort_by(Axis.Z)[0]
combined = chamfer(bottom_face.edges(), chamfer_distance)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2)
]

for x, y in hole_positions:
    combined = combined - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 1)

pocket_depth = 2.0
pocket_width = rib_width
pocket_length = base_width - 6.0
pocket = Pos(0, 0, base_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
combined = combined - pocket

part = combined
part.name = "base_plate_with_rib"
export_step(part, "output.step")