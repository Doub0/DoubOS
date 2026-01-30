extends CharacterBody2D


@export var type: String

@onready var body = $body


func _physics_process(delta):
	# Add the gravity.
	pass


func _on_chat_detection_area_body_entered(body):
	pass # Replace with function body.


func _on_chat_detection_area_body_exited(body):
	pass # Replace with function body.

func entity(type,direction):
	if type == "Cop":
		var body = $body
		if has_node("torso"):
			var face = $face
			var eye = $eyes
			var mouth = $mouth
			var hat = $hat
			var torso = $torso
			var pants = $pants
			remove_child(face)
			remove_child(eye)
			remove_child(mouth)
			remove_child(hat)
			remove_child(torso)
			remove_child(pants)
		if direction == "east":
			body.flip_h = false
			body.play("cop_e")
		elif direction == "west":
			body.flip_h = true
			body.play("cop_e")
		elif direction == "north":
			body.flip_h = false
			body.play("cop_n")
		elif direction == "south":
			body.flip_h = false
			body.play("cop_s")
		elif direction == "check":
			body.flip_h = false
			body.play("cop_check")

	if type == "Soldier":
		if has_node("body"):
			var body = $body
			remove_child(body)
		if direction == "south":
			var face = $face
			var eye = $eyes
			var mouth = $mouth
			var hat = $hat
			var torso = $torso
			var pants = $pants
			
			face.play("default")
			eye.play("green_eyes")
			mouth.play("default")
			hat.play("fed_helmet_s")
			torso.play("fed_uniform_s")
