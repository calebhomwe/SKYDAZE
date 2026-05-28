extends Node2D
class_name LaneRenderer
## Dual-plane lane rails — floor + sky (Arcaea-style).

const LANE_COUNT := 4
const LANE_WIDTH := 140.0
const FLOOR_HIT_Y := 560.0
const SKY_HIT_Y := 160.0

var fever_t := 0.0
var shake_strength: float = 0.0
var _lane_pulse := {"floor": [0.0, 0.0, 0.0, 0.0], "sky": [0.0, 0.0, 0.0, 0.0]}


func _process(delta: float) -> void:
	fever_t += delta
	shake_strength = lerpf(shake_strength, 0.0, delta * 8.0)
	position.x = sin(fever_t * 40.0) * shake_strength
	for plane in _lane_pulse.keys():
		var arr: Array = _lane_pulse[plane]
		for i in arr.size():
			arr[i] = maxf(0.0, arr[i] - delta * 4.0)
	queue_redraw()


func hit_line_y(plane: String) -> float:
	return SKY_HIT_Y if plane == "sky" else FLOOR_HIT_Y


func lane_x(lane: float, viewport_width: float) -> float:
	var total := LANE_WIDTH * float(LANE_COUNT)
	var start_x := (viewport_width - total) * 0.5
	return start_x + LANE_WIDTH * (lane + 0.5)


func trigger_shake(amount: float = 4.0) -> void:
	shake_strength = maxf(shake_strength, amount)


func pulse_lane(plane: String, lane: int, strength: float = 1.0) -> void:
	if not _lane_pulse.has(plane):
		return
	var arr: Array = _lane_pulse[plane]
	if lane < 0 or lane >= arr.size():
		return
	arr[lane] = maxf(arr[lane], strength)


func _draw_plane(vp: Vector2, hit_y: float, top_y: float, base_col: Color, glow_col: Color, fever: float, plane: String) -> void:
	var pulses: Array = _lane_pulse.get(plane, [0.0, 0.0, 0.0, 0.0])
	for i in LANE_COUNT:
		var x: float = lane_x(float(i), vp.x)
		draw_line(Vector2(x, top_y), Vector2(x, hit_y + 30), base_col, 2.0)
		var lane_pulse_v: float = float(pulses[i]) if i < pulses.size() else 0.0
		var glow := glow_col * Color(1, 1, 1, 0.08 + fever * 0.14 + lane_pulse_v * 0.35)
		var width: float = 4.0 + lane_pulse_v * 6.0
		draw_line(Vector2(x - 1, top_y), Vector2(x - 1, hit_y + 30), glow, width)
		if lane_pulse_v > 0.05:
			var ring := glow_col * Color(1, 1, 1, lane_pulse_v * 0.5)
			draw_circle(Vector2(x, hit_y), 14.0 + lane_pulse_v * 24.0, ring)
	var pulse: float = 0.5 + 0.5 * sin(fever_t * 4.0)
	var hit_col := Color(1.0, 1.0, 1.0, 0.35 + pulse * 0.25 + fever * 0.2)
	draw_line(Vector2(40, hit_y), Vector2(vp.x - 40, hit_y), hit_col, 3.0)


func _draw() -> void:
	var vp: Vector2 = get_viewport_rect().size
	var fever: float = 1.0 if GameState.fever_active else 0.0
	_draw_plane(vp, SKY_HIT_Y, 60.0, Color(0.2, 0.12, 0.35, 0.7), Color(0.85, 0.35, 1.0, 1.0), fever, "sky")
	_draw_plane(vp, FLOOR_HIT_Y, 300.0, Color(0.1, 0.14, 0.28, 0.65), Color(0.0, 0.85, 1.0, 1.0), fever, "floor")
	# Plane labels
	draw_string(ThemeDB.fallback_font, Vector2(48, SKY_HIT_Y - 12), "SKY", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.85, 0.55, 1.0, 0.55))
	draw_string(ThemeDB.fallback_font, Vector2(48, FLOOR_HIT_Y - 12), "FLOOR", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.4, 0.85, 1.0, 0.55))
