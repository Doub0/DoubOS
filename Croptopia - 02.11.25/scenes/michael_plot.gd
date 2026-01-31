extends Node2D

var player

var redbaneberry = preload("res://redbaneberry.tscn")
var construction_table = preload("res://scenes/Placeables/construction_table.tscn")
var chives = preload("res://chive.tscn")
var yes = false
var has_baneberry = false

var placeable
var cutscene_happened = false

@onready var cutscene_numb = 0

signal baneberry_placed

var can_build = false

@onready var build_ui = $build_ui/CanvasLayer/Sprite2D

@onready var anim = $build_ui/CanvasLayer/AnimationPlayer

@onready var placeable_item = $placement_mechanic/redbane_placeable

var item_variant
#var mouse_tile = get_global_mouse_position()
func _ready():
#	player = $player
	build_mode(false)
	cutscene_start()
	
	
func _on_play_pressed():
	pass
func _process(delta):
	print("SIGMAAAA",$placement_mechanic.get_children())
#	$phillip_merchant.shop_open()
#	print("IS PROCESSING IN PLOT?",$phillip_merchant.process_mode)
#	print(can_build, get_children())
	placeable = $placement_mechanic/redbane_placeable
	if !can_build or player.selected_item == null:
		placeable.process_mode = Node.PROCESS_MODE_DISABLED#
	if can_build:
		if player.selected_item == "Redbaneberry":
			placeable.process_mode = Node.PROCESS_MODE_ALWAYS
			print("selected redbaneberry!")
			Tilemanager.tilemap = $placement_mechanic/TileMap
			placeable.variant(player.selected_item)
	#		selected_redbane = true
	#		chive_collected = false
	#		selected_chives = false
			if Input.is_action_just_pressed("Right-Click") or Input.is_action_just_pressed("left click"):
				var redbaneberry_instance = redbaneberry.instantiate()
				add_child(redbaneberry_instance)
				redbaneberry_instance.position = $placement_mechanic/redbane_placeable.position
				emit_signal("redbane_placed")
				print("working like usual")
		
		#############################################
	#	if chive_collected == true:
	#		Tilemanager.tilemap = $test2/TileMap
	#		$test2/chive_placeable.visible = true
	#		$test2/redbane_placeable.visible = false
	#		selected_chives = true
	#		redbane_collected = false
	#		selected_redbane = false
		if player.selected_item == "Chive":
			placeable.process_mode = Node.PROCESS_MODE_ALWAYS
			print("selected chives!")
			Tilemanager.tilemap = $placement_mechanic/TileMap
			placeable.variant(player.selected_item)
	#		selected_chives = true
	#		redbane_collected = false
	#		selected_redbane = false
			if Input.is_action_just_pressed("Right-Click") or Input.is_action_just_pressed("left click"):
				var chive_instance = chives.instantiate()
				add_child(chive_instance)
				chive_instance.position = $placement_mechanic/redbane_placeable.position
				emit_signal("chive_placed")
				print("working like usual")
		else:
			pass

func _on_redbaneberry_picked_up():
		custom()
#			if Input.is_action_just_pressed("Right-Click"):
#				add_child(object_test)
#				object_test.position = Vector2(0,0)
##		await get_tree().create_timer(3).timeout
#
#
#
#func _on_timer_timeout():
#	Tilemanager.tilemap = $TileMap
#	$testobj.visible = true
#	if Input.is_action_just_pressed("Right-Click"):
#			add_child(object_test)
#			object_test.position = Vector2(0,0)
#
#	await get_tree().create_timer(3).timeout
	
func _input(event):
   # Mouse in viewport coordinates.
	if event is InputEventMouseButton:
		if item_variant == "":
			print("INPUT POS",event.position)
			var redbaneberry_instance = redbaneberry.instantiate()
			add_child(redbaneberry_instance)
			redbaneberry_instance.position = $placement_mechanic/redbane_placeable.position
			
			emit_signal("baneberry_placed")
		
		if item_variant == "Construction Table":
			var redbaneberry_instance = construction_table.instantiate()
			add_child(redbaneberry_instance)
			redbaneberry_instance.position = $placement_mechanic/redbane_placeable.position
			

func custom():
	Tilemanager.tilemap = $placement_mechanic/TileMap
	$placement_mechanic/redbane_placeable.visible = true
	yes = true
	if Input.is_action_just_pressed("Right-Click"):
		var redbaneberry_instance = redbaneberry.instantiate()
		add_child(redbaneberry_instance)
		redbaneberry_instance.position = $placement_mechanic/redbane_placeable.position

func cutscene_start():
	$dialogue.visible = true
	$dialogue/zea.visible = true
	$dialogue/Sprite2D.visible = true

func _on_third_zea_dialogue_dialogue_finished():
#	$dialogue/Sprite2D/first_philip_dialogue.visible = true
	$dialogue/zea/third_zea_dialogue.visible = false
	
	
func cutscene_end():
	$dialogue.visible = false
	$dialogue/zea.visible = false
	$dialogue/Sprite2D.visible = false
	
	cutscene_happened = true

func _on_first_philip_dialogue_dialogue_finished():
	cutscene_end()


func _on_entry_body_entered(body):
	if body.has_method("player"):
		player = body
		build_mode(true)
		initializing()

func _on_entry_body_exited(body):
	if body.has_method("player"):
		build_mode(false)
		initializing()

func build_mode(variant: bool):
	can_build = variant
	if variant == true:
		placeable = $placement_mechanic/redbane_placeable
		build_ui.visible = variant
		Tilemanager.tilemap = $TileMap
		$placement_mechanic/redbane_placeable.visible = true
		$ColorRect.visible = true
		anim.play("fade")
#		$placement_mechanic/chive_placeable.visible = false
		player.connect("item_holding", Callable(self, "build_initializer"))
		
	else:
		anim.play("RESET")
		build_ui.visible = variant
		placeable = $placement_mechanic/redbane_placeable
	return can_build
		
func initializing():
	if cutscene_happened:
		$dialogue/Sprite2D/first_philip_dialogue.visible = false
		$dialogue/zea/third_zea_dialogue.visible = false
	else:
		pass

func build_initializer():
	item_variant = player.item_type
	build_variant(item_variant)
	
func build_variant(variant):
	placeable_item.variant(variant)
