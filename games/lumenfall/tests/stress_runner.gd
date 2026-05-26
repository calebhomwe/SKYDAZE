extends Node
## Headless stress harness — spawns dense charts and verifies stability.

const OUTPUT_PATH := "/workspace/artifacts/lumenfall/stress_result.json"
const NOTE_COUNTS := [200, 500, 1000]
const MAX_FRAMES := 120000

var _player
var _suite_index := 0
var _frames := 0
var _started_ms := 0
var _results: Array = []


func _ready() -> void:
	_started_ms = Time.get_ticks_msec()
	_player = preload("res://scripts/gameplay/BeatmapPlayer.gd").new()
	_player.auto_start = false
	_player.headless_simulate = true
	add_child(_player)
	_player.chart_finished.connect(_on_chart_finished)
	_run_next_suite()


func _run_next_suite() -> void:
	if _suite_index >= NOTE_COUNTS.size():
		_write_results(true)
		get_tree().quit(0)
		return
	var count: int = NOTE_COUNTS[_suite_index]
	print("Stress suite: spawn %d notes" % count)
	_player.run_stress_spawn(count)


func _on_chart_finished(summary: Dictionary) -> void:
	_results.append({
		"note_count": NOTE_COUNTS[_suite_index],
		"frames": _frames,
		"elapsed_ms": Time.get_ticks_msec() - _started_ms,
		"summary": summary,
		"pass": summary.get("accuracy", 0.0) >= 50.0,
	})
	_suite_index += 1
	_run_next_suite()


func _process(_delta: float) -> void:
	_frames += 1
	if _frames > MAX_FRAMES:
		push_error("Stress timeout")
		_write_results(false)
		get_tree().quit(1)


func _write_results(ok: bool) -> void:
	var payload := {
		"ok": ok,
		"engine": "godot",
		"suites": _results,
		"total_frames": _frames,
	}
	var dir := DirAccess.open("/workspace/artifacts/lumenfall")
	if dir == null:
		DirAccess.make_dir_recursive_absolute("/workspace/artifacts/lumenfall")
	var file := FileAccess.open(OUTPUT_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(payload, "\t"))
		print("Wrote ", OUTPUT_PATH)
