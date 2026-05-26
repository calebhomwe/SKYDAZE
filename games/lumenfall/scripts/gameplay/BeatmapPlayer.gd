extends Node2D
class_name BeatmapPlayer
## Spawns notes from chart JSON, handles input + judgements.

const NoteNodeClass = preload("res://scripts/gameplay/NoteNode.gd")
const JudgementSystemClass = preload("res://scripts/gameplay/JudgementSystem.gd")
const LaneRendererClass = preload("res://scripts/gameplay/LaneRenderer.gd")

signal chart_finished(summary: Dictionary)

const SCROLL_SPEED := 0.55  # px per ms
const NOTE_POOL_MAX := 256

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


func _ready() -> void:
	_lanes = LaneRendererClass.new()
	add_child(_lanes)
	_setup_particles()
	_load_chart(chart_id)
	if auto_start and not headless_simulate:
		call_deferred("start_run")


func _setup_particles() -> void:
	_hit_particles = CPUParticles2D.new()
	_hit_particles.emitting = false
	_hit_particles.one_shot = true
	_hit_particles.amount = 24
	_hit_particles.lifetime = 0.45
	_hit_particles.explosiveness = 0.95
	_hit_particles.direction = Vector2(0, -1)
	_hit_particles.spread = 120.0
	_hit_particles.gravity = Vector2(0, 180)
	_hit_particles.initial_velocity_min = 80.0
	_hit_particles.initial_velocity_max = 220.0
	_hit_particles.scale_amount_min = 0.4
	_hit_particles.scale_amount_max = 1.2
	_hit_particles.color = Color(0.2, 0.95, 1.0, 0.9)
	add_child(_hit_particles)


func _load_chart(id: String) -> void:
	chart_id = id
	_chart = ChartLibrary.load_chart(id)
	_notes_raw = _chart.get("notes", [])
	_notes_raw.sort_custom(func(a, b): return float(a.get("t", 0)) < float(b.get("t", 0)))


func start_run() -> void:
	GameState.reset_run()
	GameState.chart_id = chart_id
	_song_ms = 0.0
	_spawn_index = 0
	_running = true
	_finished = false
	for n in _active:
		_recycle_note(n)
	_active.clear()


func _process(delta: float) -> void:
	if not _running:
		return
	GameState.tick_fever(delta)
	_song_ms += delta * 1000.0
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
		if float(data.get("t", 0)) > _song_ms + 2200.0:
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
		var y: float = _lanes.HIT_LINE_Y - (note.hit_time_ms - _song_ms) * SCROLL_SPEED
		note.position = Vector2(x, y)
		note.visible = y > -40 and y < vp.y + 40


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
			_try_hit_lane(lane)


func _try_hit_lane(lane: int) -> void:
	var best = null
	var best_delta: float = INF
	for note in _active:
		if note.consumed:
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
	_burst_at(note.position, kind)
	_active.erase(note)
	_recycle_note(note)


func _register_miss(note) -> void:
	if note.consumed:
		return
	note.consumed = true
	GameState.register_judgement("miss", 0)


func _burst_at(pos: Vector2, kind: String) -> void:
	_hit_particles.position = pos
	match kind:
		"pure":
			_hit_particles.color = Color(1.0, 0.95, 0.7, 0.95)
		"great":
			_hit_particles.color = Color(0.2, 0.95, 1.0, 0.9)
		_:
			_hit_particles.color = Color(0.85, 0.35, 1.0, 0.85)
	_hit_particles.restart()


func _simulate_inputs() -> void:
	for note in _active:
		if note.consumed:
			continue
		var delta: float = note.hit_time_ms - _song_ms
		if delta <= 0 and delta > -8:
			var lane: int = int(round(note.current_lane_at(_song_ms)))
			_try_hit_lane(lane)


func _finish_chart() -> void:
	_finished = true
	_running = false
	GameState.commit_high_score()
	chart_finished.emit({
		"chart_id": chart_id,
		"score": GameState.score,
		"max_combo": GameState.max_combo,
		"accuracy": GameState.accuracy_percent(),
		"grade": GameState.letter_grade(),
		"judgements": GameState.judgements.duplicate(),
	})


func run_stress_spawn(count: int) -> void:
	_notes_raw.clear()
	for i in count:
		var entry: Dictionary = {"t": 500 + i * 35, "lane": i % 4, "type": "tap"}
		if i % 5 == 0:
			entry["type"] = "hold"
			entry["end_t"] = 500 + i * 35 + 300
		_notes_raw.append(entry)
	_spawn_index = 0
	start_run()
	headless_simulate = true
