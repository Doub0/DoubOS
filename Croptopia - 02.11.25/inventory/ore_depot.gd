extends Node2D

var state = NO_ORE

var player

var has_entered = false
var mined = false

var iron = preload("res://inventory/iron_ore.tres")
var coal = preload("res://inventory/coal.tres")

@export var item: InvItem

@onready var state_texture = $AnimatedSprite2D

enum {
	NO_ORE,
	IRON,
	COAL
}
# Called when the node enters the scene tree for the first time.
func _ready():
	generate_ore()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	match state:
		NO_ORE:
			state_texture.play("no_ores")
			mined = true
		IRON:
			state_texture.play("iron_ore")
		COAL:
			state_texture.play("coal_ore")
	if has_entered == true:
		if mined == false:
			if Input.is_action_just_pressed("e"):
				pick()
				player.collect(item)
				mined = true
				print("ITS COLLECTED")
	if mined == true:
		state = NO_ORE
		
func choose(array):
	array.shuffle()
	return array.front()
	
func pick():
	if state == IRON:
		item = iron
	elif state == COAL:
		item = coal
		
func generate_ore():
	state = choose([NO_ORE, IRON, COAL])

func _on_area_2d_body_entered(body):
	print("SOMETHING... has entered the area")
	if body.has_method("player"):
		player = body
		has_entered = true
