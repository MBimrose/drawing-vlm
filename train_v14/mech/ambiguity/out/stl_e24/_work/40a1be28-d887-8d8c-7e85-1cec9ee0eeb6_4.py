from build123d import *

base_radius = 20.0
base_height = 30.0
flange_width = 60.0
flange_depth = 40.0
flange_thickness = 8.0
transition_steps = 4
step_height = base_height / transition_steps
radius_decrement = (base_radius - flange_width / 2) / transition_steps
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    for i in range(transition_steps + 1):
        z = i * step_height
        r = base_radius - i * radius_decrement
        with BuildSketch(Plane.XY.offset(z)) as s:
            Circle(r)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, base_height + flange_thickness / 2) * Box(flange_width, flange_depth, flange_thickness)
solid_body = solid_body - Pos(0, 0, (base_height + flange_thickness) / 2) * Cylinder(central_hole_diameter / 2, base_height + flange_thickness + 10)

for x, y in [(-mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (-mount_hole_spacing_x / 2, mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, mount_hole_spacing_y / 2)]:
    solid_body = solid_body - Pos(x, y, base_height + flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_base_with_flange"
export_step(part, "output.step")