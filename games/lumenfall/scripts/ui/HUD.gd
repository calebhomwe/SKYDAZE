extends CanvasLayer
## HUD — score, combo, fever, accuracy (Arcaea readability).

@onready var _score: Label = $Root/TopBar/Score
@onready var _combo: Label = $Root/TopBar/Combo
@onready var _acc: Label = $Root/TopBar/Accuracy
@onready var _fever: Label = $Root/FeverBanner
@onready var _title: Label = $Root/TopBar/Title
@onready var _grade: Label = $Root/Results/Grade
@onready var _results: PanelContainer = $Root/Results


func _ready() -> void:
	GameState.score_changed.connect(_on_score)
	GameState.combo_changed.connect(_on_combo)
	GameState.fever_changed.connect(_on_fever)
	GameState.judgement_registered.connect(_on_judgement)
	_results.visible = false
	_fever.visible = false
	_on_score(GameState.score)
	_on_combo(0)


func bind_chart(chart: Dictionary) -> void:
	_title.text = "%s — %s" % [chart.get("title", "?"), chart.get("artist", "?")]


func show_results(summary: Dictionary) -> void:
	_results.visible = true
	_grade.text = "GRADE %s\n%d pts\n%.1f%% acc\n%d combo" % [
		summary.get("grade", "?"),
		int(summary.get("score", 0)),
		float(summary.get("accuracy", 0.0)),
		int(summary.get("max_combo", 0)),
	]


func _on_score(v: int) -> void:
	_score.text = "%d" % v


func _on_combo(v: int) -> void:
	_combo.text = "%dx" % v if v > 1 else ""
	_combo.modulate = Color(1, 0.85, 0.4) if v >= 50 else Color(1, 1, 1)


func _on_fever(active: bool) -> void:
	_fever.visible = active
	_fever.text = "RAPTURE CHAIN"


func _on_judgement(kind: String) -> void:
	_acc.text = "%.1f%%" % GameState.accuracy_percent()
	if kind == "pure":
		_combo.modulate = Color(1.0, 0.95, 0.7)
