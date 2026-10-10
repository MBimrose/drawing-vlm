from build123d import *
sleeve_length = 60.0
flange_length = 10.0
outer_radius = 20.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
flange_radius = 30.0
chamfer_size = 2.0
inlet_hole_diameter = 6.0
inlet_hole_offset = 12.0
mount_hole_diameter = 4.0
mount_hole_count = 4
with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((outer_radius, 0), (outer_radius, sleeve_length))
            Line((outer_radius, sleeve_length), (flange_radius, sleeve_length))
            Line((flange_radius, sleeve_length), (flange_radius, sleeve_length + flange_length))
            Line((flange_radius, sleeve_length + flange_length), (inner_radius, sleeve_length + flange_length))
            Line((inner_radius, sleeve_length + flange_length), (inner_radius, 0))
            Line((inner_radius, 0), (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)
solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)
import math
inlet_cyl = Pos(0, inlet_hole_offset, sleeve_length/2) * Rot(0, 90, 0) * Cylinder(inlet_hole_diameter/2, 2*outer_radius)
solid_body = solid_body - inlet_cyl
mount_radius = flange_radius - wall_thickness/2
for i in range(mount_hole_count):
    theta = math.radians(i * 360.0 / mount_hole_count)
    px = mount_radius * math.cos(theta)
    py = mount_radius * math.sin(theta)
    solid_body = solid_body - Pos(px, py, (sleeve_length + flange_length)/2) * Cylinder(mount_hole_diameter/2, sleeve_length + flange_length)
part = solid_body
part.name = "sleeve_with_flange"
export_step(part, OUTPUT_PATH)