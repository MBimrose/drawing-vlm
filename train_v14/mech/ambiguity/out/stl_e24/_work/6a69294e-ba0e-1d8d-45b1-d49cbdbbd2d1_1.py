from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
taper_length = 20.0
taper_height = 8.0
slot_width = 2.0
slot_length = lever_length * 0.8
hole_diameter = 4.0
hole_spacing = 12.0
hole_count = 3
chamfer_distance = 1.0
rib_width = 5.0
rib_height = 2.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (lever_length, 0), (lever_length, lever_width - taper_height),
                     (lever_length - taper_length, lever_width), (0, lever_width), close=True)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

slot = Pos(lever_length/2, lever_width/2, lever_thickness/2) * Box(slot_length, slot_width, lever_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = lever_length/2 + (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(x, lever_width/2, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness)
    solid_body = solid_body - hole

rib_count = int((lever_length - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count):
    x = rib_spacing + i * rib_spacing
    rib = Pos(x, lever_width/2, lever_thickness/2) * Box(rib_width, rib_height, lever_thickness)
    solid_body = solid_body + rib

right_face = solid_body.faces().sort_by(Axis.X)[-1]
chamfer_edges = right_face.edges().filter_by(Axis.Z)
solid_body = chamfer(chamfer_edges, chamfer_distance)

part = solid_body
part.name = "lever"
export_step(part, "output.step")