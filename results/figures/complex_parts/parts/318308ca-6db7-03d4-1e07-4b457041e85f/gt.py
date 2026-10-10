from build123d import *

outer_width = 40.0
outer_length = 80.0
extrude_thickness = 15.0
notch_width = 10.0
notch_depth = 5.0
shell_thickness = 4.0
chamfer_distance = 1.0
slot_width = 8.0
slot_length = 60.0
slot_depth = 5.0
hole_diameter = 4.0
hole_depth = 10.0
csk_angle = 82.0
hole_spacing = 25.0
hole_rows = 1
hole_columns = 3

p1 = (-outer_width/2, -outer_length/2)
p2 = ( outer_width/2, -outer_length/2)
p3 = ( outer_width/2, -notch_depth)
p4 = ( outer_width/2 - notch_width, -notch_depth)
p5 = ( outer_width/2 - notch_width,  outer_length/2)
p6 = (-outer_width/2,  outer_length/2)
points = [p1, p2, p3, p4, p5, p6]

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline(*points, close=True)
        make_face()
    extrude(amount=extrude_thickness)
solid = p.part

top_edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid = chamfer(top_edges, chamfer_distance)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-shell_thickness, openings=[top_face])

slot_body = Pos(0, 0, extrude_thickness - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid = solid - slot_body

for i in range(hole_columns):
    x = (i - (hole_columns - 1) / 2) * hole_spacing
    hole = Pos(x, outer_length/2, extrude_thickness/2) * Rot(-90, 0, 0) * CounterSinkHole(hole_diameter/2, 10.0, hole_depth, csk_angle)
    solid = solid - hole

part = solid
part.name = "TSlotBracket"
export_step(part, OUTPUT_PATH)