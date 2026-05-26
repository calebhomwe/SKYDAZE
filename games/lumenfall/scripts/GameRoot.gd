extends Node
## Game scene — gameplay + HUD, returns to menu on finish.

@onready var _gameplay = $Gameplay
@onready var _hud = $HUD


func _ready() -> void:
	var id: String = GameState.chart_id if GameState.chart_id != "" else "first_light"
	_gameplay.chart_id = id
	_gameplay.load_chart(id)
	var chart: Dictionary = ChartLibrary.load_chart(_gameplay.chart_id)
	_hud.bind_chart(chart)
	_gameplay.chart_finished.connect(_on_chart_finished)


func _on_chart_finished(summary: Dictionary) -> void:
	_hud.show_results(summary)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://scenes/Menu.tscn")
	if event.is_action_pressed("retry"):
		get_tree().reload_current_scene()
