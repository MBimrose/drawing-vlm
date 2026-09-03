from build123d import *

bracket_width = 80.0
bracket_height = 60.0
bracket_thickness = 12.0
wall_thickness = 5.0
top_fillet_radius = 12.0
hole_diameter = 6.0
hole_spacing = 30.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 3.0
edge_fillet = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-bracket_width/2, -bracket_height/2), (bracket_width/2, -bracket_height/2))
            l2 = Line(l1@1, (bracket_width/2, bracket_height/2 - top_fillet_radius))
            a1 = ThreePointArc(l2@1, (0, bracket_height/2 + top_fillet_radius), (-bracket_width/2, bracket_height/2 - top_fillet_radius))
            l3 = Line(a1@1, (-bracket_width/2, -bracket_height/2))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_width = bracket_width - 2 * wall_thickness
inner_height = bracket_height - 2 * wall_thickness
pocket_depth = bracket_thickness - wall_thickness

with BuildPart() as pp:
    with BuildSketch() as psk:
        with BuildLine() as pbl:
            pl1 = Line((-inner_width/2, -inner_height/2), (inner_width/2, -inner_height/2))
            pl2 = Line(pl1@1, (inner_width/2, inner_height/2 - top_fillet_radius))
            pa1 = ThreePointArc(pl2@1, (0, inner_height/2 + top_fillet_radius), (-inner_width/2, inner_height/2 - top_fillet_radius))
            pl3 = Line(pa1@1, (-inner_width/2, -inner_height/2))
        make_face()
    extrude(amount=pocket_depth)

pocket_solid = Pos(0, 0, bracket_thickness - pocket_depth) * pp.part
solid_body = solid_body - pocket_solid

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

solid_body = solid_body - Pos(0, 0, slot_depth/2) * Box(slot_width, slot_length, slot_depth)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")