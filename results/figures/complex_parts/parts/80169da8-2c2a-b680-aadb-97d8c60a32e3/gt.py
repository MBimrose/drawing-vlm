from build123d import *

outer_width = 80.0
height = 30.0
wall_thickness = 2.0
outer_radius = outer_width / 2.0
inner_radius = outer_radius - wall_thickness
vent_width = 20.0
vent_height = 10.0
vent_offset_z = (height - vent_height) / 2.0
chamfer_dist = 0.5
mount_hole_dia = 3.0
mount_hole_spacing = 40.0
rib_thickness = 2.0
rib_width = 10.0
rib_height = 5.0
panel_thickness = wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

front_panel = Pos(0, outer_radius, 0) * Box(2 * inner_radius, panel_thickness, height)
front_panel = chamfer(front_panel.edges(), chamfer_dist)
solid_body = solid_body + front_panel

vent_box = Pos(outer_radius - wall_thickness / 2.0, vent_offset_z + vent_height / 2.0, 0) * Box(wall_thickness + 0.2, vent_width, vent_height)
solid_body = solid_body - vent_box

for x, z in [(-mount_hole_spacing / 2.0, vent_offset_z + vent_height / 2.0),
             (mount_hole_spacing / 2.0, vent_offset_z + vent_height / 2.0)]:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia / 2.0, 100)

for angle in [0, 90, 180, 270]:
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness + 0.1, rib_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "revolved_enclosure"
export_step(part, OUTPUT_PATH)