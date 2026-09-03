from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
pocket_chamfer = 2.0
hole_diameter = 5.0
hole_cbore_diameter = 6.0
hole_cbore_depth = 2.0
hole_spacing = 20.0
rib_height = 4.0
rib_thickness = 3.0
rib_offset = 10.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket_edges = pocket.edges().filter_by(Axis.Z)
pocket = chamfer(pocket_edges, pocket_chamfer)
result = result - pocket

hole_positions = [
    (0, -hole_spacing),
    (-hole_spacing * 1.5, hole_spacing),
    (hole_spacing * 1.5, hole_spacing)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)

rib1 = Pos(0, -plate_width/4, -plate_thickness/2 - rib_height/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
rib2 = Pos(0, plate_width/4, -plate_thickness/2 - rib_height/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
result = result + rib1 + rib2

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")