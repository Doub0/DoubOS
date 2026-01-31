extends StaticBody2D

@export var direction: String
@export var variant: String

@onready var texture = $texture

# Called when the node enters the scene tree for the first time.
func _ready():
	if direction == "Single":
		texture.texture = preload("res://assets/Item Assets/placeables/spruce_fence_single.png")
	elif direction == "Down":
		texture.texture = preload("res://assets/Item Assets/placeables/spruce_fence_grouped.png")
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	
