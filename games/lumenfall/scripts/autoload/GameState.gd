extends Node
## Global run state: score, combo, fever, daily meta, persistence.

const FEVER_COMBO_THRESHOLD := 50
const FEVER_DURATION_SEC := 10.0
const DAILY_CLEAR_GOAL := 3
const SAVE_PATH := "user://lumenfall_scores.json"
const META_PATH := "user://lumenfall_meta.json"

var chart_id: String = "first_light"
var score: int = 0
var combo: int = 0
var max_combo: int = 0
var fever_active: bool = false
var fever_time_left: float = 0.0
var judgements := {"pure": 0, "great": 0, "good": 0, "miss": 0}
var high_scores: Dictionary = {}

var daily_streak: int = 0
var clears_today: int = 0
var last_play_day: String = ""
var total_clears: int = 0
var unlocked: Array = ["first_light"]

signal score_changed(new_score: int)
signal combo_changed(new_combo: int)
signal fever_changed(active: bool)
signal judgement_registered(kind: String)
signal meta_changed


func _ready() -> void:
	_load_scores()
	_load_meta()
	_roll_daily()


func reset_run() -> void:
	score = 0
	combo = 0
	max_combo = 0
	fever_active = false
	fever_time_left = 0.0
	judgements = {"pure": 0, "great": 0, "good": 0, "miss": 0}
	score_changed.emit(score)
	combo_changed.emit(combo)
	fever_changed.emit(false)


func register_judgement(kind: String, points: int) -> void:
	judgements[kind] = int(judgements.get(kind, 0)) + 1
	var multiplier := 2.0 if fever_active else 1.0
	if kind == "miss":
		combo = 0
		if fever_active:
			_end_fever()
	else:
		combo += 1
		max_combo = max(max_combo, combo)
		score += int(round(points * multiplier))
		if not fever_active and combo >= FEVER_COMBO_THRESHOLD:
			_start_fever()
	score_changed.emit(score)
	combo_changed.emit(combo)
	judgement_registered.emit(kind)


func _start_fever() -> void:
	fever_active = true
	fever_time_left = FEVER_DURATION_SEC
	fever_changed.emit(true)


func _end_fever() -> void:
	fever_active = false
	fever_time_left = 0.0
	fever_changed.emit(false)


func tick_fever(delta: float) -> void:
	if not fever_active:
		return
	fever_time_left -= delta
	if fever_time_left <= 0.0:
		_end_fever()


func accuracy_percent() -> float:
	var total := 0
	for k in judgements:
		total += int(judgements[k])
	if total == 0:
		return 100.0
	var weighted: float = (
		float(judgements.pure) * 100.0
		+ float(judgements.great) * 80.0
		+ float(judgements.good) * 50.0
	) / float(total)
	return weighted


func letter_grade() -> String:
	var acc := accuracy_percent()
	if acc >= 98.0:
		return "P"
	if acc >= 95.0:
		return "S"
	if acc >= 90.0:
		return "A"
	if acc >= 80.0:
		return "B"
	if acc >= 70.0:
		return "C"
	return "D"


func commit_high_score() -> void:
	var prev: int = int(high_scores.get(chart_id, 0))
	if score > prev:
		high_scores[chart_id] = score
		_save_scores()


func record_clear(grade: String) -> void:
	total_clears += 1
	var today := _utc_day()
	if last_play_day == today:
		clears_today += 1
	else:
		if last_play_day != "":
			daily_streak += 1
		else:
			daily_streak = 1
		last_play_day = today
		clears_today = 1
	_unlock_progression(grade)
	_save_meta()
	meta_changed.emit()


func daily_mission_progress() -> Dictionary:
	return {
		"goal": DAILY_CLEAR_GOAL,
		"clears": clears_today,
		"complete": clears_today >= DAILY_CLEAR_GOAL,
		"streak": daily_streak,
	}


func is_unlocked(id: String) -> bool:
	return unlocked.has(id)


func _unlock_progression(grade: String) -> void:
	if chart_id == "first_light" and grade in ["B", "A", "S", "P"]:
		if not unlocked.has("rapture_chain"):
			unlocked.append("rapture_chain")
	if chart_id == "rapture_chain" and grade in ["A", "S", "P"]:
		if not unlocked.has("void_surge"):
			unlocked.append("void_surge")


func _utc_day() -> String:
	var dt := Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02d" % [dt.year, dt.month, dt.day]


func _is_yesterday(day: String) -> bool:
	if day == "":
		return false
	var parts := day.split("-")
	if parts.size() != 3:
		return false
	var y := int(parts[0])
	var m := int(parts[1])
	var d := int(parts[2])
	d -= 1
	if d < 1:
		m -= 1
		if m < 1:
			m = 12
			y -= 1
		d = 28
	return _utc_day() != day


func _roll_daily() -> void:
	var today := _utc_day()
	if last_play_day != "" and last_play_day != today and not _is_yesterday(last_play_day):
		daily_streak = 0
		clears_today = 0


func _load_scores() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		return
	var parsed = JSON.parse_string(file.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		high_scores = parsed


func _save_scores() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		return
	file.store_string(JSON.stringify(high_scores, "\t"))


func _load_meta() -> void:
	if not FileAccess.file_exists(META_PATH):
		return
	var file := FileAccess.open(META_PATH, FileAccess.READ)
	if file == null:
		return
	var parsed = JSON.parse_string(file.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	daily_streak = int(parsed.get("daily_streak", 0))
	clears_today = int(parsed.get("clears_today", 0))
	last_play_day = str(parsed.get("last_play_day", ""))
	total_clears = int(parsed.get("total_clears", 0))
	var u = parsed.get("unlocked", ["first_light"])
	if typeof(u) == TYPE_ARRAY:
		unlocked = u


func _save_meta() -> void:
	var file := FileAccess.open(META_PATH, FileAccess.WRITE)
	if file == null:
		return
	file.store_string(JSON.stringify({
		"daily_streak": daily_streak,
		"clears_today": clears_today,
		"last_play_day": last_play_day,
		"total_clears": total_clears,
		"unlocked": unlocked,
	}, "\t"))
