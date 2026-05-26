extends Node
## Loads chart JSON from res://data/charts.

const CHART_DIR := "res://data/charts/"


func list_chart_ids() -> Array[String]:
	var ids: Array[String] = []
	var dir := DirAccess.open(CHART_DIR)
	if dir == null:
		return ids
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		if not dir.current_is_dir() and name.ends_with(".json"):
			ids.append(name.get_basename())
		name = dir.get_next()
	dir.list_dir_end()
	ids.sort()
	return ids


func load_chart(chart_id: String) -> Dictionary:
	var path := CHART_DIR + chart_id + ".json"
	if not FileAccess.file_exists(path):
		push_error("Chart not found: %s" % path)
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {}
	var data = JSON.parse_string(file.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return {}
	return data
