from build123d import *

outer_radius = 20.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
total_length = 100.0
vent_slot_length = 30.0
vent_slot_width = 1.5
vent_slot_depth = wall_thickness + 0.5
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, 0), (outer_radius, 0))
            Line((outer_radius, 0), (outer_radius, total_length))
            Line((outer_radius, total_length), (inner_radius, total_length))
            Line((inner_radius, total_length), (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot = Pos(outer_radius - vent_slot_depth/2, 0, total_length/2) * Box(vent_slot_depth, vent_slot_width, vent_slot_length)
solid_body = solid_body - slot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, total_length/2) * Cylinder(mount_hole_diameter/2, total_length)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_vent_slot"
export_step(part, "output.step")