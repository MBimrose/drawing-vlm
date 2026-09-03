from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 3.0
pocket_chamfer = 2.0
hole_diameter = 5.0
hole_cbore_diameter = 6.0
hole_cbore_depth = 2.0
hole_offset = 15.0
rib_height = 4.0
rib_thickness = 3.0
rib_spacing = 30.0

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

pocket_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
                if abs(e.center().X) <= pocket_length/2 + 0.1 and abs(e.center().Y) <= pocket_width/2 + 0.1]
solid_body = chamfer(pocket_edges, pocket_chamfer)

hole_positions = [(hole_offset, hole_offset), (-hole_offset, hole_offset), (0, -hole_offset)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

rib_length = plate_length - 2 * rib_spacing
rib1 = Pos(0, rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(0, -rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")