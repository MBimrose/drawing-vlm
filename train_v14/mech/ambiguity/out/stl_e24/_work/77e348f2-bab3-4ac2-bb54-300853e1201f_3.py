from build123d import *

base_length = 80.0
height = 60.0
extrude_length = 30.0
wall_thickness = 3.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_depth = 12.0
pocket_offset = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_length, 0), (base_length/2, height), close=True)
        make_face()
    extrude(amount=extrude_length)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = offset(solid_body, amount=-wall_thickness, openings=solid_body.faces())

pocket_box = Box(pocket_depth, extrude_length - 2*wall_thickness, pocket_width)
pocket_box = Pos(pocket_offset + pocket_depth/2, 0, extrude_length/2) * pocket_box
solid_body = solid_body - pocket_box

hole_cyl = Cylinder(mount_hole_diameter/2, extrude_length + 10)
hole1 = Pos(base_length/2 - mount_hole_spacing/2, mount_hole_offset, extrude_length/2) * hole_cyl
hole2 = Pos(base_length/2 + mount_hole_spacing/2, mount_hole_offset, extrude_length/2) * hole_cyl
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "triangular_prism_shell"
export_step(part, "output.step")