from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 80.0
leg_thickness = 8.0
bracket_width = 20.0
inner_fillet_radius = 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 4.0
pocket_offset_x = 10.0
pocket_offset_y = 15.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 6.0
rib_length = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_width)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X) < 1e-6 and abs(e.center().Y) < 1e-6]
solid_body = fillet(inner_edges, inner_fillet_radius)

pocket = Pos(pocket_offset_x, pocket_offset_y, bracket_width - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(horizontal_leg_length/2 - hole_spacing/2, leg_thickness/2),
             (horizontal_leg_length/2 + hole_spacing/2, leg_thickness/2)]:
    shaft = Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_width + 1)
    cbore = Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - shaft - cbore

rib = Pos(leg_thickness/2, vertical_leg_length + rib_length/2, bracket_width/2) * Box(rib_thickness, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")