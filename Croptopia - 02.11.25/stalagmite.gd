extends Node2D

var state = CHIPPED

var player

var has_entered = false
var mined = false

@export var item: InvItem

@onready var state_texture = $AnimatedSprite2D

enum {
	CHIPPED,
	ELONGATED
}
# Called when the node enters the scene tree for the first time.
func _ready():
	generate_ore()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	match state:
		CHIPPED:
			state_texture.play("chipped")
		ELONGATED:
			state_texture.play("elongated")
	if has_entered == true:
		if mined == false:
			if Input.is_action_just_pressed("e"):
				player.collect(item)
				mined = true
				print("ITS COLLECTED")
	if mined == true:
		state = CHIPPED
		
func choose(array):
	array.shuffle()
	return array.front()
		
func generate_ore():
	state = choose([CHIPPED, ELONGATED])

func _on_area_2d_body_entered(body):
	print("SOMETHING... has entered the area")
	if body.has_method("player"):
		player = body
		has_entered = true
