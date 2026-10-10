from build123d import *
import math

# ---- dimensions from drawing (mm) ----
flange_dia = 80.0
flange_t = 4.3
hub_dia = 45.7
hub_t = 7.1
boss_dia = 31.4
boss_t = 11.4
shaft_dia = 14.3
shaft_len = 40.0
groove_dia = 71.4          # 1x O 71.4 x 4.3 DEEP
groove_depth = 4.3
slot_across_flats = 14.3   # 14.3 A/F
slot_count = 4
slot_len = 22.0
slot_width = 4.0

flange_r = flange_dia / 2.0
hub_r = hub_dia / 2.0
boss_r = boss_dia / 2.0
shaft_r = shaft_dia / 2.0
groove_r = groove_dia / 2.0

# ---- revolved solid (axis along Y) ----
with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine():
            Polyline((0, 0),
                     (flange_r, 0),
                     (flange_r, flange_t),
                     (hub_r, flange_t),
                     (hub_r, flange_t + hub_t),
                     (boss_r, flange_t + hub_t),
                     (boss_r, flange_t + hub_t + boss_t),
                     (shaft_r, flange_t + hub_t + boss_t),
                     (shaft_r, flange_t + hub_t + boss_t + shaft_len),
                     (0, flange_t + hub_t + boss_t + shaft_len),
                     close=True)
        make_face()
    revolve(axis=Axis.Y)

solid = p.part

# ---- 1x O 71.4 x 4.3 DEEP groove in the flange face ----
groove_cyl = Pos(0, groove_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(groove_r, groove_depth)
solid = solid - groove_cyl

# ---- radial slots through the flange (4x, 14.3 A/F) ----
slot_center_x = flange_r - slot_len / 2.0
for i in range(slot_count):
    angle_deg = 360.0 / slot_count * i
    slot = Rot(0, angle_deg, 0) * Pos(slot_center_x, flange_t / 2, 0) * Box(slot_len, flange_t, slot_width)
    solid = solid - slot

part = solid
part.name = "pulley"
export_step(part, "output.step")