extends ColorRect
## Animated nebula background — swaps intensity during fever.

@export var shader_path: Shader = preload("res://shaders/nebula_bg.gdshader")

var _mat: ShaderMaterial


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	color = Color(0.02, 0.02, 0.05, 1)
	_mat = ShaderMaterial.new()
	_mat.shader = shader_path
	material = _mat
	GameState.fever_changed.connect(_on_fever)


func _process(delta: float) -> void:
	if _mat == null:
		return
	var t := Time.get_ticks_msec() / 1000.0
	_mat.set_shader_parameter("time_sec", t)
	_mat.set_shader_parameter("fever", 1.0 if GameState.fever_active else 0.0)


func _on_fever(_active: bool) -> void:
	pass
