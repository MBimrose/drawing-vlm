from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
corner_radius = 15.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 1.0
hole_diameter = 4.0
hole_offset = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
mount_hole_offset = 12.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_length, 0))
            l2 = Line(l1 @ 1, (plate_length, plate_width - corner_radius))
            a1 = RadiusArc(l2 @ 1, (plate_length - corner_radius, plate_width), corner_radius)
            l3 = Line(a1 @ 1, (0, plate_width))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

rib = Pos(plate_length/2, plate_width/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for x, y in [(hole_offset, hole_offset), (plate_length - hole_offset, hole_offset),
             (hole_offset, plate_width - hole_offset), (plate_length - hole_offset, plate_width - hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

for x, y in [(plate_length/2, mount_hole_offset), (plate_length/2, plate_width - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")