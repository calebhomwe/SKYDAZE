extends Node
## App router: menu -> game loop.

const GAME_SCENE := "res://scenes/Game.tscn"


func _ready() -> void:
	get_tree().change_scene_to_file("res://scenes/Menu.tscn")


func go_play(chart_id: String) -> void:
	var err := get_tree().change_scene_to_file(GAME_SCENE)
	if err != OK:
		push_error("Failed to load game scene")
		return
	await get_tree().process_frame
	var game := get_tree().current_scene
	if game and game.has_method("set"):
		game.set("chart_id", chart_id)
