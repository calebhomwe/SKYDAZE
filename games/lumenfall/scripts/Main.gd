extends Node
## Main scene coordinator.

@onready var _gameplay = $Gameplay
@onready var _hud = $HUD


func _ready() -> void:
	var chart := ChartLibrary.load_chart("first_light")
	if _hud.has_method("bind_chart"):
		_hud.bind_chart(chart)
	_gameplay.chart_finished.connect(_on_chart_finished)


func _on_chart_finished(summary: Dictionary) -> void:
	if _hud.has_method("show_results"):
		_hud.show_results(summary)


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		get_tree().quit()
