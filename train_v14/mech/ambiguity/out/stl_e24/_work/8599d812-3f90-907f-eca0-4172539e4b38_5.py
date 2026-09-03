from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
rib_height = 2.0
rib_width = 10.0
rib_offset = 5.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
chamfer_size = 0.5
fillet_radius = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part

rib = Pos(0, plate_width/2 - rib_offset - rib_width/2, plate_thickness/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
base = base + rib

pocket = Pos(0, 0, plate_thickness/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole_r = mount_hole_diameter / 2
hole_h = plate_thickness + 2
for x, y in [(-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
             ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
             (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
             ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)]:
    base = base - Pos(x, y, plate_thickness/2) * Cylinder(hole_r, hole_h)

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

part = base
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")