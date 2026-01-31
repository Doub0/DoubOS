extends Node2D

@onready var player = $player
@onready var NPC = $scenes/npc
@onready var camera = $player/Camera2D

var spawn
var mysterious_confrontation
var shelburne_road
var first_zea_scene
var shelburne
var mount_crag
var top_of_mount_crag
var michael_plot
var inside_zea_scene
var cave
var zea

var zea_walk_scene

var zea_second_cutscene

var ui

var quest_is_finished = false
var is_pathfollowing = false
var is_pathfollowing2 = false
var cutscene_is_over = false

var is_openingcutscene = false #Asks if the opening cutscene is active

var has_player_entered_area = false #Asks if the player has entered the Area

var is_henryfollowing = false #The camera is not following a path?
var is_henryfollowing2 = false

var zea_house_happened = "false"

var redbaneberry = preload("res://redbaneberry.tscn")
var chives = preload("res://chive.tscn")
var yes = false

var has_baneberry = false
var has_chives = false

var selected_redbane = false
var selected_chives = false
var redbane_collected = false
var chive_collected = false

var day_count

var sunset_time
var sunrise_time

var night_time
var day_time

var phase

signal disable_building
#####################
var cutscene_happened = false
var cutscene_numb = 0

var redbane_sold
var chive_sold
var pinecone_sold

@export var redbane = 0
@export var chive = 0
@export var pinecone = 0

func _ready():
#	zea_walk_cutscene()
	var spawn_file = preload("res://scenes/spawn_node.tscn")
	var spawn_instance = spawn_file.instantiate()
	add_child(spawn_instance)
	spawn = spawn_instance
	spawn.connect("scene_triggered", Callable(self, "generate_shelburne_road"))
#	spawn.mysterious_cutscene.player = player
	var ui_file = preload("res://scenes/ui.tscn")
	var ui_instance = ui_file.instantiate()
	add_child(ui_instance)
	ui = ui_instance
	
#	var p_file = preload("res://phillip_merchant.tscn")
#	var p_instance = p_file.instantiate()
#	add_child(p_instance)

func _process(delta):
	$CanvasLayer/Label.text = str(int(player.global_position.x)," ", int(player.global_position.y), "// In scene coords: ",int(player.position.x * 2.75)," ",int(player.position.y / -2.5))
#	print(get_viewport().get_camera_2d())
#	print(get_viewport().get_camera_2d().get_parent())
#	if self.has_node("shelburnroad"):
#		if (shelburne_road.position - player.position) > Vector2(250,-900):
#			shelburne_road.process_mode = Node.PROCESS_MODE_DISABLED
#		if (shelburne_road.position - player.position) < Vector2(250,-900):
#			shelburne_road.process_mode = Node.PROCESS_MODE_ALWAYS
#	if self.has_node("spawn_node"):
#		if (spawn.position.x + player.position.x) > 500 or (spawn.position.y + player.position.y) > -1200:
#			spawn.process_mode = Node.PROCESS_MODE_ALWAYS
#			spawn.show()
#
#		elif (spawn.position.x + player.position.x) < 500 or (spawn.position.y + player.position.y) < -1200:
#			spawn.process_mode = Node.PROCESS_MODE_DISABLED
#			spawn.hide()
	if self.has_node("npc"):
#		print(zea.timer.paused)
#		print(zea.position.y - player.position.y)
		if (zea.position.y - player.position.y) > -300:
			zea.timer.paused = false
#			(zea.position.x - player.position.x) < 300 or zea.show()
#
		elif (zea.position.y - player.position.y) < -300:
			zea.current_state = 0
			zea.timer.paused = true
#			zea.hide()(zea.position.x - player.position.x) > 300 or 

	if Input.is_action_just_pressed("arrow_right"):
		player.position = Vector2(-2845,-2789)
		generate_shelburne_road()
		
	if Input.is_action_just_pressed("Extra_key1"):
		player.position = Vector2(-4603,-1959)
		generate_shelburne()
	
func _physics_process(_delta):
	pass
	
func _on_npc_quest_is_finished():
	print("DONE")
	quest_is_finished = true
	player.position = Vector2(-1000,0)
	is_pathfollowing = true
	zea_walk_cutscene()

func _on_npc_quest_quest_finished():
	quest_is_finished = true
	player.position = Vector2(-1000,0)
	is_pathfollowing = true
	zea_walk_cutscene()

func generate_shelburne_road():
	if !self.has_node("shelburnroad"):
		var shelburne_road_file = preload("res://testing.tscn")
		var shelburne_road_instance = shelburne_road_file.instantiate()
		shelburne_road_instance.position = Vector2(-3200,-2949)
		add_child(shelburne_road_instance)
		shelburne_road_instance.connect("shelburne_generate", Callable(self, "generate_shelburne"))
		shelburne_road = shelburne_road_instance
		shelburne_road_instance.player = $player
		
		
		generate_zea()
	else:
		pass
func zea_walk_cutscene():
	var zea_walking_scen_file = preload("res://scenes/zea_walk_cutscene.tscn")
	var zea_walk_instance = zea_walking_scen_file.instantiate()
	add_child(zea_walk_instance)
	zea_walk_instance.position = Vector2(-297,-1287)
	zea_walk_scene = zea_walk_instance
	zea_walk_scene.connect("cutscene_over", Callable(self, "second_zea_cutscene"))
#	zea_walk_instance.quest_camera.enabled = true
	player.camera.enabled = false
	spawn.mysterious_cutscene.camera.enabled = false

func generate_zea():
	var zea_file = preload("res://scenes/npc.tscn")
	var zea_instance = zea_file.instantiate()
	add_child(zea_instance)
	zea = zea_instance
	zea.connect("quest_is_finished", Callable(self, "_on_npc_quest_is_finished"))
	zea.position = Vector2(-297,-1287)
	zea.z_index = 2
func second_zea_cutscene():
	var second_zea_file = preload("res://scenes/scenetwo.tscn")
	var second_zea_instance = second_zea_file.instantiate()
	second_zea_instance.player = player
	second_zea_instance.position = Vector2(-5091.517, -3156.3)
	second_zea_instance.connect("cutscene_finished", Callable(self, "second_zea_over"))
	zea_second_cutscene = second_zea_instance
	add_child(second_zea_instance)
	remove_child(zea_walk_scene) #REMOVE LATER AND MAKE IT FREE ITSELF AND DEPOSIT INFO TO SAVE FILE
	
func second_zea_over():
	print("DEACTIVATE")
	deactivate_cams(player.camera,zea_second_cutscene.cutscene_cam,spawn.mysterious_cutscene.camera)
	zea_second_cutscene.queue_free()
	generate_shelburne()
func deactivate_cams(variant1,variant2,variant3):
	variant1.enabled = true
	variant2.enabled = false
	variant3.enabled = false
func generate_shelburne():
	if !self.has_node("shelburne"):
		var shelburne_file = preload("res://shelburne.tscn")
		var shelburne_instance = shelburne_file.instantiate()
		add_child(shelburne_instance)
		shelburne = shelburne_instance
		shelburne.position = Vector2(-10388,-1849)
		
		shelburne_instance.connect("mt_crag_over", Callable(self, "mt_crag_cutscene_over"))
	else:
		pass
func generate_michael_plot():
	if !self.has_node("michael_plot"):
		var michael_plot_file = preload("res://scenes/michael_plot.tscn")
		var michael_plot_instance = michael_plot_file.instantiate()
		add_child(michael_plot_instance)
		michael_plot = michael_plot_instance
		michael_plot.position = Vector2(-2845,-2985)
	else:
		pass

func mt_crag_cutscene_over():
	print("SEX2")
	player.position = Vector2(-2845,-2985)
