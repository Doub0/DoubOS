extends StaticBody2D

var type = NONE

@onready var state_texture = $anim

# Called when the node enters the scene tree for the first time.
enum {
	NONE,
	FLOWER_1,
	ACORN,
	FLOWER_BUNDLE_1,
	FLOWER_BUNDLE_2,
	GRASS,
	STUB
}
func _ready():
	generate_type()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	match type:
		FLOWER_1:
			state_texture.play("flower_1")
		ACORN:
			state_texture.play("acorn")
		FLOWER_BUNDLE_1:
			state_texture.play("flower_bundle_1")
		FLOWER_BUNDLE_2:
			state_texture.play("flower_bundle_2")
		GRASS:
			state_texture.play("grass")
		STUB:
			state_texture.play("stub")

func generate_type():
	type = choose([FLOWER_1, ACORN, FLOWER_BUNDLE_1, FLOWER_BUNDLE_2, GRASS, STUB])
	
func choose(array):
	array.shuffle()
	return array.front()
