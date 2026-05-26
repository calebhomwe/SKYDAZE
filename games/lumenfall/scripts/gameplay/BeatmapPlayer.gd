extends Node2D
class_name BeatmapPlayer
## Spawns notes from chart JSON, dual-plane input, audio-synced timing.

const NoteNodeClass = preload("res://scripts/gameplay/NoteNode.gd")
const JudgementSystemClass = preload("res://scripts/gameplay/JudgementSystem.gd")
const LaneRendererClass = preload("res://scripts/gameplay/LaneRenderer.gd")

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
var _hit_particles: CPUParticles2D
var _sky_particles: CPUParticles2D


func _ready() -> void:
	_lanes = LaneRendererClass.new()
	add_child(_lanes)
	_setup_particles()
	load_chart(chart_id)
	if auto_start and not headless_simulate:
		call_deferred("start_run")


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
	return _pool.pop_back()


func _recycle_note(note) -> void:
	if note.get_parent():
		note.get_parent().remove_child(note)
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


func _unhandled_input(event: InputEvent) -> void:
	if headless_simulate or not _running:
		return
	for lane in 4:
		if event.is_action_pressed("lane_%d" % lane):
			_try_hit_lane(lane, "floor")
		if event.is_action_pressed("sky_lane_%d" % lane):
			_try_hit_lane(lane, "sky")


func _try_hit_lane(lane: int, plane: String) -> void:
	var best = null
	var best_delta: float = INF
	for note in _active:
		if note.consumed or note.plane != plane:
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
			var delta_ms: float = absf(_song_ms - note.hit_time_ms)
			if delta_ms < best_delta and delta_ms <= JudgementSystemClass.WINDOW_GOOD_MS:
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
		if _song_ms >= best.end_time_ms - JudgementSystemClass.WINDOW_GOOD_MS:
			_resolve_hit(best, kind)
	else:
		_resolve_hit(best, kind)


func _resolve_hit(note, kind: String) -> void:
	note.consumed = true
	note.pulse()
	GameState.register_judgement(kind, JudgementSystemClass.points_for(kind))
	_burst_at(note.position, kind, note.plane)
	if kind == "pure":
		_lanes.trigger_shake(5.0 if note.plane == "floor" else 3.0)
	_active.erase(note)
	_recycle_note(note)


func _register_miss(note) -> void:
	if note.consumed:
		return
	note.consumed = true
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
		var delta: float = note.hit_time_ms - _song_ms
		if delta <= 0 and delta > -8:
			var lane: int = int(round(note.current_lane_at(_song_ms)))
			_try_hit_lane(lane, note.plane)


func _finish_chart() -> void:
	_finished = true
	_running = false
	BeatEngine.stop()
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
