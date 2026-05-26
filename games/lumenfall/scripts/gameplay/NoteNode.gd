extends Node2D
class_name NoteNode
## Single chart note — tap, hold, lumen arc (floor or sky plane).

enum NoteType { TAP, HOLD, ARC, FLICK }

var note_type: NoteType = NoteType.TAP
var plane: String = "floor"
var lane: int = 0
var lane_end: int = 0
var hit_time_ms: float = 0.0
var end_time_ms: float = 0.0
var consumed: bool = false
var holding: bool = false

var _radius := 18.0
var _glow := 0.0
var _trail: Array[Vector2] = []


func setup(data: Dictionary) -> void:
	lane = int(data.get("lane", 0))
	plane = str(data.get("plane", "floor")).to_lower()
	if plane not in ["floor", "sky"]:
		plane = "floor"
	var t := str(data.get("type", "tap")).to_lower()
	match t:
		"hold":
			note_type = NoteType.HOLD
			end_time_ms = float(data.get("end_t", hit_time_ms + 500))
		"arc":
			note_type = NoteType.ARC
			lane_end = int(data.get("lane_end", lane))
			end_time_ms = float(data.get("end_t", hit_time_ms + 400))
		"flick":
			note_type = NoteType.FLICK
		_:
			note_type = NoteType.TAP
	hit_time_ms = float(data.get("t", 0))


func current_lane_at(song_ms: float) -> float:
	if note_type != NoteType.ARC:
		return float(lane)
	if end_time_ms <= hit_time_ms:
		return float(lane)
	var p := clampf((song_ms - hit_time_ms) / (end_time_ms - hit_time_ms), 0.0, 1.0)
	return lerpf(float(lane), float(lane_end), p)


func _process(delta: float) -> void:
	_glow = lerpf(_glow, 0.0, delta * 6.0)
	queue_redraw()


func pulse() -> void:
	_glow = 1.0
	queue_redraw()


func _draw() -> void:
	var base_col := Color(0.0, 0.94, 1.0, 0.95)
	if plane == "sky":
		base_col = Color(0.85, 0.45, 1.0, 0.95)
	if note_type == NoteType.HOLD:
		base_col = Color(1.0, 0.75, 0.2, 0.95)
	elif note_type == NoteType.ARC:
		base_col = Color(0.85, 0.35, 1.0, 0.95) if plane == "floor" else Color(1.0, 0.55, 0.95, 0.95)
	elif note_type == NoteType.FLICK:
		base_col = Color(1.0, 0.35, 0.55, 0.95)
	var glow_col := base_col.lightened(0.35 + _glow * 0.4)
	draw_circle(Vector2.ZERO, _radius + 8.0 * _glow, glow_col * Color(1, 1, 1, 0.28))
	draw_circle(Vector2.ZERO, _radius, base_col)
	if note_type == NoteType.HOLD:
		draw_rect(Rect2(-_radius, -_radius * 2.5, _radius * 2.0, _radius * 5.0), base_col * Color(1, 1, 1, 0.35))
	if note_type == NoteType.FLICK:
		draw_line(Vector2(-14, 0), Vector2(14, 0), Color(1, 1, 1, 0.9), 3.0)
		draw_line(Vector2(0, -14), Vector2(0, 14), Color(1, 1, 1, 0.9), 3.0)
