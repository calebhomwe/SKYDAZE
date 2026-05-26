extends RefCounted
class_name JudgementSystem
## Arcaea-style timing windows (ms).

const WINDOW_PURE_MS := 25.0
const WINDOW_GREAT_MS := 50.0
const WINDOW_GOOD_MS := 80.0

const POINTS := {
	"pure": 1000,
	"great": 700,
	"good": 400,
	"miss": 0,
}


static func judge_delta_ms(delta_ms: float) -> String:
	var ad := absf(delta_ms)
	if ad <= WINDOW_PURE_MS:
		return "pure"
	if ad <= WINDOW_GREAT_MS:
		return "great"
	if ad <= WINDOW_GOOD_MS:
		return "good"
	return "miss"


static func points_for(kind: String) -> int:
	return int(POINTS.get(kind, 0))
