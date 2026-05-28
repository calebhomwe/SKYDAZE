extends Control
## Song select + daily mission hub.

signal chart_selected(chart_id: String)

@onready var _list: VBoxContainer = $Panel/Margin/VBox/ChartList
@onready var _streak: Label = $Panel/Margin/VBox/Meta/Streak
@onready var _mission: Label = $Panel/Margin/VBox/Meta/Mission


func _ready() -> void:
	if not GameState.meta_changed.is_connected(_refresh_meta):
		GameState.meta_changed.connect(_refresh_meta)
	_build_list()
	_refresh_meta()


func _build_list() -> void:
	for c in _list.get_children():
		c.queue_free()
	for id in ChartLibrary.list_chart_ids():
		var chart: Dictionary = ChartLibrary.load_chart(id)
		var btn := Button.new()
		var locked: bool = not GameState.is_unlocked(id)
		var hs: int = int(GameState.high_scores.get(id, 0))
		btn.text = "%s%s — %s  [HS %d]" % [
			"🔒 " if locked else "",
			chart.get("title", id),
			chart.get("difficulty", "?"),
			hs,
		]
		btn.disabled = locked
		btn.pressed.connect(_on_pick.bind(id))
		_list.add_child(btn)


func _on_pick(id: String) -> void:
	GameState.chart_id = id
	get_tree().change_scene_to_file("res://scenes/Game.tscn")


func _refresh_meta() -> void:
	var m: Dictionary = GameState.daily_mission_progress()
	_streak.text = "Daily streak: %d days" % int(m.get("streak", 0))
	_mission.text = "Mission: clear %d/%d songs today%s" % [
		int(m.get("clears", 0)),
		int(m.get("goal", 3)),
		" ✓" if m.get("complete", false) else "",
	]
