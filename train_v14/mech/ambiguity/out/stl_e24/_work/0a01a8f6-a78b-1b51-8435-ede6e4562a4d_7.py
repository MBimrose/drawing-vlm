from build123d import *

base_length = 80.0
base_width = 30.0
base_thickness = 5.0
leg_height = 30.0
leg_thickness = 5.0
extrude_depth = 10.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_depth = 5.0
pocket_offset = 10.0
hole_diameter = 5.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (base_length,0), (base_length,base_thickness),
                     (leg_thickness,base_thickness), (leg_thickness,leg_height),
                     (0,leg_height), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_center_x = base_length / 2 - pocket_offset
pocket_center_y = base_thickness / 2
pocket = Pos(pocket_center_x, pocket_center_y, extrude_depth - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

hole_center_x = leg_thickness / 2
hole_center_y = leg_height / 2
hole = Pos(hole_center_x, hole_center_y, extrude_depth/2) * Cylinder(hole_diameter/2, extrude_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket_with_pocket_and_hole"
export_step(part, "output.step")