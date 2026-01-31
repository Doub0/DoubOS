extends Node2D

@export var type: String
# Called when the node enters the scene tree for the first time.
func _ready():
	if type == "Mayor":
		pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func mayor_event(variant:int):
	pass
