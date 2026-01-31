extends CanvasLayer


@export_file("*.json") var d_file

signal dialogue_finished

var dialogue = []
var current_dialogue_id = 0
var d_active = false

var dialogue_amount
var modulation
var person_name

var custom_dialogue_mode = false

var current_dialogue = 0

var custom_dialogue_1
var custom_dialogue_2
var custom_dialogue_3
var custom_dialogue_4
var custom_dialogue_5
var custom_dialogue_6
var custom_dialogue_7
var custom_dialogue_8

@onready var self_canvas = $NinePatchRect
func _ready():
	$NinePatchRect.visible = false
	
#	start()
func _process(delta):
#	print(modulation)
#	print("Custom dialogue",current_dialogue)
	if custom_dialogue_mode:
		if Input.is_action_just_pressed("enter"):
			print("ENTER")
			next_dialogue()
#			display()

func start():
	if d_active:
		return
	d_active = true
	$NinePatchRect.visible = true
	dialogue = load_dialogue()
	current_dialogue_id = -1
	next_script()
	
func load_dialogue():
	var file = FileAccess.open("res://dialouge/zea_dialogue.json", FileAccess.READ)
	var content = JSON.parse_string(file.get_as_text())
	return content
	
func _input(event):
	if !d_active:
		return
	if d_active:
		if event.is_action_pressed("enter"):
			next_script()

func next_script():
	current_dialogue_id += 1
	if current_dialogue_id >= len(dialogue):
		d_active = false
		$NinePatchRect.visible = false
		emit_signal("dialogue_finished")
		return
		
	$NinePatchRect/Name.text = dialogue[current_dialogue_id]['name']
	$NinePatchRect/Text.text = dialogue[current_dialogue_id]['text']


func _on_timer_timeout():
	$NinePatchRect.visible = true

func custom_dialogue(modulate,person,dialogue_ids):
#	current_dialogue_id = 1
	custom_dialogue_mode = true
	dialogue_amount = dialogue_ids
	person_name = person
	modulation = modulate
	display()

func next_dialogue():
	print("NEXT DIALOGUE")
	$NinePatchRect.visible = true
	current_dialogue += 1
	display()
	if current_dialogue > dialogue_amount:
		$NinePatchRect.visible = false
		emit_signal("dialogue_finished")
		return
	
func display():
	print("DISPLAY")
	$NinePatchRect.visible = true
	$NinePatchRect/Name.text = person_name
	
	$NinePatchRect.self_modulate = modulation
	if current_dialogue == 1:
		$NinePatchRect/Text.text = custom_dialogue_1
	if current_dialogue == 2:
		$NinePatchRect/Text.text = custom_dialogue_2
	if current_dialogue == 3:
		$NinePatchRect/Text.text = custom_dialogue_3
	if current_dialogue == 4:
		$NinePatchRect/Text.text = custom_dialogue_4
	if current_dialogue == 5:
		$NinePatchRect/Text.text = custom_dialogue_5
	if current_dialogue == 6:
		$NinePatchRect/Text.text = custom_dialogue_6
	if current_dialogue == 7:
		$NinePatchRect/Text.text = custom_dialogue_7
	if current_dialogue == 8:
		$NinePatchRect/Text.text = custom_dialogue_8
		
func dialogue_content(dialogue_1,dialogue_2,dialogue_3,dialogue_4,dialogue_5,dialogue_6,dialogue_7,dialogue_8):
	$NinePatchRect.visible = true
	custom_dialogue_1 = dialogue_1
	custom_dialogue_2 = dialogue_2
	custom_dialogue_3 = dialogue_3
	custom_dialogue_4 = dialogue_4
	custom_dialogue_5 = dialogue_5
	custom_dialogue_6 = dialogue_6
	custom_dialogue_7 = dialogue_7
	custom_dialogue_8 = dialogue_8
	
	return
func force_visible():
	$NinePatchRect.visible = true
