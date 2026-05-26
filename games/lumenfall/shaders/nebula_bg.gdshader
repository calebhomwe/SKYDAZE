shader_type canvas_item;

uniform float time_sec = 0.0;
uniform float fever = 0.0;

void fragment() {
	vec2 uv = UV;
	float wave = sin(uv.x * 8.0 + time_sec * 0.6) * 0.04;
	wave += sin(uv.y * 6.0 - time_sec * 0.45) * 0.03;
	vec3 deep = vec3(0.02, 0.03, 0.08);
	vec3 cyan = vec3(0.0, 0.55, 0.85);
	vec3 gold = vec3(0.95, 0.75, 0.35);
	float band = smoothstep(0.15, 0.85, uv.y + wave);
	vec3 col = mix(deep, cyan * 0.35, band);
	float streak = pow(max(0.0, sin(uv.x * 24.0 + time_sec * 1.2)), 8.0);
	col += vec3(0.15, 0.35, 0.65) * streak * (0.25 + fever * 0.55);
	col = mix(col, gold, fever * 0.25 * smoothstep(0.3, 0.9, uv.y));
	COLOR = vec4(col, 1.0);
}
