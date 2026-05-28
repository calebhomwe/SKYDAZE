extends CanvasLayer
class_name HitFeedback
## Floating judgement popups at hit position.

const LIFETIME := 0.45

var _entries: Array = []


func show_hit(world_pos: Vector2, kind: String) -> void:
	var label := Label.new()
	label.text = kind.to_upper()
	label.add_theme_font_size_override("font_size", 22 if kind == "pure" else 18)
	match kind:
		"pure":
			label.modulate = Color(1.0, 0.95, 0.65)
		"great":
			label.modulate = Color(0.3, 0.95, 1.0)
		"good":
			label.modulate = Color(0.85, 0.55, 1.0)
		_:
			label.modulate = Color(1, 0.4, 0.4)
	add_child(label)
	label.position = world_pos + Vector2(-30, -40)
	_entries.append({"node": label, "t": LIFETIME})


func _process(delta: float) -> void:
	var i := _entries.size() - 1
	while i >= 0:
		var e: Dictionary = _entries[i]
		e["t"] = float(e["t"]) - delta
		var label: Label = e["node"]
		label.position.y -= delta * 60.0
		label.modulate.a = clampf(float(e["t"]) / LIFETIME, 0.0, 1.0)
		if float(e["t"]) <= 0.0:
			label.queue_free()
			_entries.remove_at(i)
		i -= 1
