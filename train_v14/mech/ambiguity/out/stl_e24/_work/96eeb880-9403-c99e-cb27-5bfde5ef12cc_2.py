from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 12.0
notch_radius = 10.0
chamfer_distance = 5.0
hole_diameter = 6.0
hole_spacing = 25.0
rib_height = 5.0
rib_width = 40.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as bl:
            l1 = Line((-plate_length/2, -plate_width/2), (plate_length/2, -plate_width/2))
            l2 = Line(l1@1, (plate_length/2, plate_width/2 - notch_radius))
            a1 = ThreePointArc(l2@1, (plate_length/2 - notch_radius, plate_width/2), (plate_length/2 - 2*notch_radius, plate_width/2))
            l3 = Line(a1@1, (-plate_length/2, plate_width/2))
            l4 = Line(l3@1, (-plate_length/2, -plate_width/2))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_notch_rib_holes"
export_step(part, "output.step")