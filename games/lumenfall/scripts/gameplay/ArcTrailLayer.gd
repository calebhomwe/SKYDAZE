extends Node2D
class_name ArcTrailLayer
## Draws lumen arc splines for active arc notes.

const NoteNodeClass = preload("res://scripts/gameplay/NoteNode.gd")
const LaneRendererClass = preload("res://scripts/gameplay/LaneRenderer.gd")
const SEGMENTS := 24

var _notes: Array = []
var _song_ms: float = 0.0
var _lanes: Node2D
var _scroll_speed: float = 0.55
var _vp_width: float = 1280.0


func configure(lanes: Node2D, scroll_speed: float) -> void:
	_lanes = lanes
	_scroll_speed = scroll_speed


func update_arcs(notes: Array, song_ms: float, vp_width: float) -> void:
	_notes = notes
	_song_ms = song_ms
	_vp_width = vp_width
	queue_redraw()


func _draw() -> void:
	if _lanes == null:
		return
	for note in _notes:
		if note.consumed or note.note_type != NoteNodeClass.NoteType.ARC:
			continue
		var hit_y: float = _lanes.call("hit_line_y", note.plane)
		var t0: float = note.hit_time_ms
		var t1: float = note.end_time_ms
		if t1 <= t0:
			continue
		var col := Color(0.85, 0.35, 1.0, 0.55) if note.plane == "floor" else Color(1.0, 0.55, 0.95, 0.55)
		var points: PackedVector2Array = PackedVector2Array()
		for i in SEGMENTS + 1:
			var p: float = float(i) / float(SEGMENTS)
			var t_ms: float = lerpf(t0, t1, p)
			var lane_f: float = lerpf(float(note.lane), float(note.lane_end), p)
			var x: float = _lanes.call("lane_x", lane_f, _vp_width)
			var y: float = hit_y - (t_ms - _song_ms) * _scroll_speed
			points.append(Vector2(x, y))
		if points.size() >= 2:
			draw_polyline(points, col * Color(1, 1, 1, 0.2), 12.0, true)
			draw_polyline(points, col, 3.5, true)
