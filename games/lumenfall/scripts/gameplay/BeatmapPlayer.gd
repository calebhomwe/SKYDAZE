extends Node2D
class_name BeatmapPlayer
## Spawns notes from chart JSON, dual-plane input, audio-synced timing.

const NoteNodeClass = preload("res://scripts/gameplay/NoteNode.gd")
const JudgementSystemClass = preload("res://scripts/gameplay/JudgementSystem.gd")
const LaneRendererClass = preload("res://scripts/gameplay/LaneRenderer.gd")
const ArcTrailLayerClass = preload("res://scripts/gameplay/ArcTrailLayer.gd")
const HitFeedbackClass = preload("res://scripts/gameplay/HitFeedback.gd")

signal chart_finished(summary: Dictionary)

const SCROLL_SPEED := 0.55

@export var chart_id: String = "first_light"
@export var auto_start: bool = true
@export var headless_simulate: bool = false

var _chart: Dictionary = {}
var _notes_raw: Array = []
var _spawn_index: int = 0
var _active: Array = []
var _pool: Array = []
var _song_ms: float = 0.0
var _running: bool = false
var _finished: bool = false
var _lanes: Node2D
var _arc_trails: Node2D
var _feedback: CanvasLayer
var _hit_particles: CPUParticles2D
var _sky_particles: CPUParticles2D
var _held: Dictionary = {}


func _ready() -> void:
	_lanes = LaneRendererClass.new()
	add_child(_lanes)
	_arc_trails = ArcTrailLayerClass.new()
	_arc_trails.configure(_lanes, SCROLL_SPEED)
	add_child(_arc_trails)
	_feedback = HitFeedbackClass.new()
	add_child(_feedback)
	_setup_particles()
	load_chart(chart_id)
	if auto_start and not headless_simulate:
		call_deferred("start_run")


func _lane_key(plane: String, lane: int) -> String:
	return "%s_%d" % [plane, lane]


func _set_held(plane: String, lane: int, down: bool) -> void:
	_held[_lane_key(plane, lane)] = down


func _is_held(plane: String, lane: int) -> bool:
	return bool(_held.get(_lane_key(plane, lane), false))


func _setup_particles() -> void:
	_hit_particles = _make_burst(Color(0.2, 0.95, 1.0, 0.9))
	_sky_particles = _make_burst(Color(0.85, 0.35, 1.0, 0.9))
	add_child(_hit_particles)
	add_child(_sky_particles)


func _make_burst(col: Color) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.emitting = false
	p.one_shot = true
	p.amount = 32
	p.lifetime = 0.5
	p.explosiveness = 0.95
	p.direction = Vector2(0, -1)
	p.spread = 140.0
	p.gravity = Vector2(0, 160)
	p.initial_velocity_min = 90.0
	p.initial_velocity_max = 260.0
	p.color = col
	return p


func load_chart(id: String) -> void:
	chart_id = id
	_chart = ChartLibrary.load_chart(id)
	_notes_raw = _chart.get("notes", [])
	_notes_raw.sort_custom(func(a, b): return float(a.get("t", 0)) < float(b.get("t", 0)))


func start_run() -> void:
	GameState.reset_run()
	GameState.chart_id = chart_id
	_song_ms = float(_chart.get("offset_ms", 0))
	_spawn_index = 0
	_running = true
	_finished = false
	_held.clear()
	for n in _active:
		_recycle_note(n)
	_active.clear()
	var bpm: float = float(_chart.get("bpm", 174))
	BeatEngine.configure(bpm, _song_ms)
	BeatEngine.set_enabled(not headless_simulate)
	BeatEngine.start()


func _process(delta: float) -> void:
	if not _running:
		return
	GameState.tick_fever(delta)
	_song_ms += delta * 1000.0
	BeatEngine.sync_ms(_song_ms)
	_spawn_due_notes()
	_update_note_positions()
	if _arc_trails:
		_arc_trails.update_arcs(_active, _song_ms, get_viewport_rect().size.x)
	_process_holds()
	_auto_miss_overdue()
	if headless_simulate:
		_simulate_inputs()
	if _spawn_index >= _notes_raw.size() and _active.is_empty() and not _finished:
		_finish_chart()


func _spawn_due_notes() -> void:
	while _spawn_index < _notes_raw.size():
		var data: Dictionary = _notes_raw[_spawn_index]
		if float(data.get("t", 0)) > _song_ms + 2400.0:
			break
		var note = _acquire_note()
		note.setup(data)
		note.consumed = false
		note.holding = false
		add_child(note)
		_active.append(note)
		_spawn_index += 1


func _acquire_note():
	if _pool.is_empty():
		return NoteNodeClass.new()
	var note = _pool.pop_back()
	if note.get_parent():
		note.get_parent().remove_child(note)
	return note


func _recycle_note(note) -> void:
	if note.get_parent():
		note.get_parent().remove_child(note)
	if note not in _pool:
		_pool.append(note)


func _update_note_positions() -> void:
	var vp: Vector2 = get_viewport_rect().size
	for note in _active:
		var lane_f: float = note.current_lane_at(_song_ms)
		var x: float = _lanes.lane_x(lane_f, vp.x)
		var hit_y: float = _lanes.hit_line_y(note.plane)
		var y: float = hit_y - (note.hit_time_ms - _song_ms) * SCROLL_SPEED
		note.position = Vector2(x, y)
		note.visible = y > -40 and y < vp.y + 40
		if note.note_type == NoteNodeClass.NoteType.ARC and not note.consumed:
			note.queue_redraw()


func _auto_miss_overdue() -> void:
	var to_remove: Array = []
	for note in _active:
		if note.consumed:
			continue
		if note.holding:
			continue
		var late_ms: float = _song_ms - note.hit_time_ms
		if note.note_type == NoteNodeClass.NoteType.HOLD:
			if _song_ms > note.end_time_ms + JudgementSystemClass.WINDOW_GOOD_MS:
				_register_miss(note)
				to_remove.append(note)
		elif late_ms > JudgementSystemClass.WINDOW_GOOD_MS:
			_register_miss(note)
			to_remove.append(note)
	for note in to_remove:
		_active.erase(note)
		_recycle_note(note)


func _process_holds() -> void:
	var to_remove: Array = []
	for note in _active:
		if not note.holding or note.consumed:
			continue
		if note.note_type != NoteNodeClass.NoteType.HOLD:
			continue
		if not _is_held(note.plane, note.lane) and _song_ms < note.end_time_ms:
			_register_miss(note)
			to_remove.append(note)
			continue
		if _song_ms >= note.end_time_ms - JudgementSystemClass.WINDOW_GOOD_MS:
			if headless_simulate or _is_held(note.plane, note.lane):
				var tail_delta: float = _song_ms - note.end_time_ms
				var tail_kind: String = JudgementSystemClass.judge_delta_ms(tail_delta)
				var kind: String = _worst_kind(note.head_kind, tail_kind)
				_resolve_hit(note, kind)
				to_remove.append(note)
	for note in to_remove:
		_active.erase(note)
		_recycle_note(note)


func _worst_kind(a: String, b: String) -> String:
	var rank := {"pure": 0, "great": 1, "good": 2, "miss": 3}
	return a if rank.get(a, 3) >= rank.get(b, 3) else b


func _unhandled_input(event: InputEvent) -> void:
	if headless_simulate or not _running:
		return
	for lane in 4:
		if event.is_action_pressed("lane_%d" % lane):
			_set_held("floor", lane, true)
			_try_hit_lane(lane, "floor")
		if event.is_action_released("lane_%d" % lane):
			_set_held("floor", lane, false)
		if event.is_action_pressed("sky_lane_%d" % lane):
			_set_held("sky", lane, true)
			_try_hit_lane(lane, "sky")
		if event.is_action_released("sky_lane_%d" % lane):
			_set_held("sky", lane, false)


func _try_hit_lane(lane: int, plane: String) -> void:
	var best = null
	var best_delta: float = INF
	for note in _active:
		if note.consumed or note.plane != plane:
			continue
		if note.holding:
			continue
		if note.note_type == NoteNodeClass.NoteType.ARC:
			var lane_now: int = int(round(note.current_lane_at(_song_ms)))
			if lane_now != lane:
				continue
			var delta_ms: float = absf(_song_ms - note.hit_time_ms)
			if delta_ms < best_delta and delta_ms <= JudgementSystemClass.WINDOW_GOOD_MS:
				best = note
				best_delta = delta_ms
		else:
			if note.lane != lane:
				continue
			var window_ms: float = JudgementSystemClass.WINDOW_GOOD_MS
			if note.note_type == NoteNodeClass.NoteType.FLICK:
				window_ms = JudgementSystemClass.WINDOW_GREAT_MS
			var delta_ms: float = absf(_song_ms - note.hit_time_ms)
			if delta_ms < best_delta and delta_ms <= window_ms:
				best = note
				best_delta = delta_ms
	if best == null:
		return
	var signed_delta: float = _song_ms - best.hit_time_ms
	var kind: String = JudgementSystemClass.judge_delta_ms(signed_delta)
	if kind == "miss":
		return
	if best.note_type == NoteNodeClass.NoteType.HOLD:
		best.holding = true
		best.head_kind = kind
		_burst_at(best.position, kind, best.plane)
		_lanes.trigger_shake(2.0)
		return
	_resolve_hit(best, kind)


func _resolve_hit(note, kind: String) -> void:
	note.consumed = true
	note.holding = false
	note.pulse()
	GameState.register_judgement(kind, JudgementSystemClass.points_for(kind))
	_burst_at(note.position, kind, note.plane)
	if _feedback:
		_feedback.show_hit(note.position, kind)
	if kind == "pure":
		_lanes.trigger_shake(5.0 if note.plane == "floor" else 3.0)
	_active.erase(note)
	_recycle_note(note)


func _register_miss(note) -> void:
	if note.consumed:
		return
	note.consumed = true
	note.holding = false
	GameState.register_judgement("miss", 0)


func _burst_at(pos: Vector2, kind: String, plane: String) -> void:
	var particles: CPUParticles2D = _sky_particles if plane == "sky" else _hit_particles
	particles.position = pos
	match kind:
		"pure":
			particles.color = Color(1.0, 0.95, 0.7, 0.95)
		"great":
			particles.color = Color(0.2, 0.95, 1.0, 0.9)
		_:
			particles.color = Color(0.85, 0.35, 1.0, 0.85)
	particles.restart()


func _simulate_inputs() -> void:
	for note in _active:
		if note.consumed:
			continue
		if note.note_type == NoteNodeClass.NoteType.HOLD:
			if not note.holding:
				var head_delta: float = note.hit_time_ms - _song_ms
				if head_delta <= 0 and head_delta > -8:
					_set_held(note.plane, note.lane, true)
					_try_hit_lane(note.lane, note.plane)
			else:
				_set_held(note.plane, note.lane, true)
			continue
		var delta: float = note.hit_time_ms - _song_ms
		if delta <= 0 and delta > -8:
			var lane: int = int(round(note.current_lane_at(_song_ms)))
			_try_hit_lane(lane, note.plane)


func _finish_chart() -> void:
	_finished = true
	_running = false
	BeatEngine.stop()
	_cleanup_notes()
	GameState.commit_high_score()
	var grade: String = GameState.letter_grade()
	GameState.record_clear(grade)
	chart_finished.emit({
		"chart_id": chart_id,
		"score": GameState.score,
		"max_combo": GameState.max_combo,
		"accuracy": GameState.accuracy_percent(),
		"grade": grade,
		"judgements": GameState.judgements.duplicate(),
		"daily": GameState.daily_mission_progress(),
	})


func run_stress_spawn(count: int) -> void:
	_notes_raw.clear()
	for i in count:
		var plane: String = "sky" if i % 3 == 0 else "floor"
		var entry: Dictionary = {
			"t": 500 + i * 35,
			"lane": i % 4,
			"plane": plane,
			"type": "tap",
		}
		if i % 7 == 0:
			entry["type"] = "arc"
			entry["lane_end"] = (i + 2) % 4
			entry["end_t"] = 500 + i * 35 + 350
		elif i % 5 == 0:
			entry["type"] = "hold"
			entry["end_t"] = 500 + i * 35 + 300
		elif plane == "sky" and i % 4 == 0:
			entry["type"] = "flick"
		_notes_raw.append(entry)
	_spawn_index = 0
	headless_simulate = true
	start_run()


func _cleanup_notes() -> void:
	for note in _active:
		_recycle_note(note)
	_active.clear()
	for note in _pool:
		if is_instance_valid(note):
			note.free()
	_pool.clear()
	_held.clear()
