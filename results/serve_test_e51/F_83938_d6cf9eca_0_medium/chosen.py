from build123d import *

overall_width = 80.0
overall_height = 60.0
overall_thickness = 15.0
pocket_width = 50.0
pocket_height = 45.0
pocket_depth = 10.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_distance = 1.0

solid_body = Box(overall_width, overall_thickness, overall_height)

pocket = Pos(0, -overall_thickness/2 + pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, overall_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "WallMountBracket"
export_step(part, "output.step")