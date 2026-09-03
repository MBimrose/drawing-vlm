from build123d import *

vertical_height = 80.0
horizontal_length = 70.0
leg_thickness = 10.0
leg_width = 20.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_count = 4
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_length,0), (horizontal_length,leg_width),
                     (leg_thickness,leg_width), (leg_thickness,vertical_height),
                     (0,vertical_height), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

slot = Pos(leg_thickness/2, vertical_height/2, leg_thickness/2) * Box(slot_width, slot_length, leg_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = leg_thickness + hole_spacing/2 + i * hole_spacing
    y = leg_width/2
    hole = Pos(x, y, leg_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")