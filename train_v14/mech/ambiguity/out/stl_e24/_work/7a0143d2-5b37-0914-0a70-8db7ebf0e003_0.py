from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_thickness = 10.0
bracket_depth = 10.0
slot_width = 5.0
slot_depth = 5.0
hole_diameter = 5.0
hole_spacing = 40.0
gusset = True
gusset_thickness = 3.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_thickness, 0), (leg_thickness, vertical_leg_length - leg_thickness),
                     (horizontal_leg_length, vertical_leg_length - leg_thickness),
                     (horizontal_leg_length, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

slot_box = Pos(horizontal_leg_length / 2, vertical_leg_length - slot_depth / 2, bracket_depth / 2) * Box(slot_width, slot_depth, bracket_depth)
solid_body = solid_body - slot_box

for x in [horizontal_leg_length / 2 - hole_spacing / 2, horizontal_leg_length / 2 + hole_spacing / 2]:
    hole = Pos(x, vertical_leg_length, bracket_depth / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 200)
    solid_body = solid_body - hole

if gusset:
    with BuildPart() as gp:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((leg_thickness, leg_thickness), (leg_thickness + gusset_thickness, leg_thickness),
                         (leg_thickness, leg_thickness + gusset_thickness), close=True)
            make_face()
        extrude(amount=bracket_depth)
    solid_body = solid_body + gp.part

outer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1]
solid_body = chamfer(outer_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")