from build123d import *

overall_length = 80.0
overall_width = 30.0
overall_height = 60.0
shoulder_length = 20.0
shoulder_width = 15.0
wall_thickness = 3.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 10.0
hole_diameter = 5.0
hole_offset_x = 10.0
hole_offset_y = 10.0
fillet_radius = 2.7

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (overall_length, 0), (overall_length, overall_width),
                     (shoulder_length, overall_width), (shoulder_length, shoulder_width),
                     (0, shoulder_width), close=True)
        make_face()
    extrude(amount=overall_height)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(overall_length/2, overall_width/2, overall_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(hole_offset_x, hole_offset_y, overall_height/2) * Cylinder(hole_diameter/2, overall_height + 10)
solid_body = solid_body - hole

part = solid_body
part.name = "stepped_block_with_pocket_and_hole"
export_step(part, "output.step")