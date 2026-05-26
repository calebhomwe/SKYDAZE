extends Node2D
class_name LaneRenderer
## Glowing lane rails (Arcaea-style readability).

const LANE_COUNT := 4
const LANE_WIDTH := 140.0
const HIT_LINE_Y := 560.0

var fever_t := 0.0


func _process(delta: float) -> void:
	fever_t += delta
	queue_redraw()


func lane_x(lane: float, viewport_width: float) -> float:
	var total := LANE_WIDTH * float(LANE_COUNT)
	var start_x := (viewport_width - total) * 0.5
	return start_x + LANE_WIDTH * (lane + 0.5)


func _draw() -> void:
	var vp := get_viewport_rect().size
	var fever := 1.0 if GameState.fever_active else 0.0
	for i in LANE_COUNT:
		var x := lane_x(float(i), vp.x)
		var col := Color(0.15, 0.2, 0.35, 0.55)
		if i % 2 == 0:
			col = Color(0.1, 0.14, 0.28, 0.65)
		draw_line(Vector2(x, 80), Vector2(x, HIT_LINE_Y + 40), col, 2.0)
		var glow := Color(0.0, 0.85, 1.0, 0.08 + fever * 0.12)
		draw_line(Vector2(x - 1, 80), Vector2(x - 1, HIT_LINE_Y + 40), glow, 4.0)
	# Hit line
	var pulse := 0.5 + 0.5 * sin(fever_t * 4.0)
	var hit_col := Color(1.0, 1.0, 1.0, 0.35 + pulse * 0.25 + fever * 0.2)
	draw_line(Vector2(40, HIT_LINE_Y), Vector2(vp.x - 40, HIT_LINE_Y), hit_col, 3.0)
