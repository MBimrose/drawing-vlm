from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
inner_fillet_radius = 4.0
counterbore_diameter = 30.0
counterbore_depth = 15.0
set_screw_diameter = 4.0
set_screw_offset = 15.0
key_slot_width = 6.0
key_slot_length = 30.0
rib_height = 20.0
rib_thickness = 3.0
rib_depth = 2.0
rib_count = 6
chamfer_size = 0.5

inner_radius = outer_diameter/2 - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_diameter/2, 0), (outer_diameter/2, length))
            l2 = Line(l1@1, (inner_radius + inner_fillet_radius, length))
            ra = RadiusArc(l2@1, (inner_radius, length - inner_fillet_radius), inner_fillet_radius)
            l3 = Line(ra@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(set_screw_offset, 0, length/2) * Cylinder(set_screw_diameter/2, length)
key_slot_thick = wall_thickness + 0.01
solid_body = solid_body - Pos(outer_diameter/2 - key_slot_thick/2, 0, 0) * Box(key_slot_thick, key_slot_length, key_slot_width)
rib_center_dist = outer_diameter/2 - wall_thickness/2 - rib_depth/2
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    solid_body = solid_body - Rot(0, 0, angle_deg) * Pos(rib_center_dist, 0, 0) * Box(rib_depth, rib_thickness, rib_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "hollow_shaft_with_features"
export_step(part, OUTPUT_PATH)