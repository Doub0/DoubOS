extends Node2D

@onready var dialogue_pos = $zea_second_dialogue_pos.position
var cutscene_pos = self.position

var player

var frame = 0
var cutscene

var entity
var dialogue_player
var sequencer

var in_cutscene = false

signal shelburne_generate

# Called when the node enters the scene tree for the first time.
func _ready():
	$AudioStreamPlayer2D.play()
	
	print("player",player)
	
	var timer = Timer.new()
	
	add_child(timer)
	timer.wait_time = 1
	timer.one_shot = true
	timer.start()
	timer.connect("timeout", Callable(self, "generate_michael_plot"))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_scenetrans_body_entered(body):
	if !in_cutscene:
		if body.has_method("player"):
			checkpoint()
	
func checkpoint():
	in_cutscene = true
	print("cutscene")
	var police_officer_file = preload("res://scenes/entities/npc_format.tscn")
	var police_instance = police_officer_file.instantiate()
	police_instance.entity("Cop","east")
	police_instance.scale = Vector2(1,1)
	police_instance.position.x = int(player.position.x + (3160))
	police_instance.position.y = int(player.position.y + (2950))
	print("EQUATION:", police_instance.position)
	print("Scene POS:", $scenetrans/CollisionShape2D.position)
	
	player.anim.play("walk_left_idle")
	player.cam_preset("CUTSCENE")
	player.player_can_move(false,true)
	
	entity = police_instance
	
	add_child(police_instance)
	
	var dialogue_loader = preload("res://dialouge/dialogue.tscn")
	var dialogue_instance = dialogue_loader.instantiate()
	
	dialogue_instance.d_active = false
#	dialogue_instance.force_visible()

	add_child(dialogue_instance)
	
	dialogue_instance.dialogue_content("Papers, please.","Sorry sir, only government agents may leave the town.","The town is encircled and the outskirts are a battlefield now.","","","","","")
	dialogue_instance.custom_dialogue(Color.hex(0x00ffff),"Cop",3)
	dialogue_instance.next_dialogue()
	
	dialogue_instance.connect("dialogue_finished", Callable(self, "checkpoint_over"))
	
	dialogue_player = dialogue_instance
	
	
	
	cutscene = "Cop"
	
	var sequence_timer = Timer.new()
	
	add_child(sequence_timer)
	sequence_timer.wait_time = 2
	sequence_timer.start()
	sequence_timer.connect("timeout", Callable(self, "sequence_timer_timeout"))
	
	sequencer = sequence_timer
	sequence_timer_timeout()
	
#	return cutscene
	
func sequence_timer_timeout():
	frame += 1
	print("frame ", frame)
	if cutscene == "Cop":
		print(" YUEEEE")
		if frame == 1:
			entity.body.play("cop_e")
			player.anim.flip_h = false
			player.anim.play("walk_left_idle")
		elif frame == 2:
			entity.body.play("cop_check")
#			dialogue_player.next_dialogue()
		elif frame == 3:
			player.anim.flip_h = false
			player.anim.play("wield_walk_w")
			player.anim.pause()
			var newspaper_spritesheet = preload("res://assets/papers_1.png")
			player.item_sprite.texture = newspaper_spritesheet
			player.item_sprite.scale = Vector2(0.3,0.3)
			player.item_sprite.position = player.item_west_pos.position
	
		elif frame == 4:
			entity.body.play("cop_e")
			player.anim.play("walk_left_idle")
			player.item_sprite.visible = false
			player.item_sprite.scale = Vector2(1,1)
	
		elif frame == 5:
			entity.body.play("cop_e")
			player.anim.play("walk_left_idle")
			player.item_sprite.visible = false
			player.item_sprite.scale = Vector2(1,1)
			dialogue_player.next_dialogue()
		elif frame == 6:
			entity.body.play("cop_e")
			player.anim.play("walk_left_idle")
			player.item_sprite.visible = false
			player.item_sprite.scale = Vector2(1,1)
			dialogue_player.next_dialogue()
		elif frame == 7:
			entity.queue_free()
			dialogue_player.queue_free()
			sequencer.queue_free()
			player.cam_preset("NORMAL")
			player.player_can_move(true,true)
			in_cutscene = false
func checkpoint_over():
	entity.queue_free()
	dialogue_player.queue_free()
	sequencer.queue_free()
	player.cam_preset("NORMAL")
	player.player_can_move(true,true)
	in_cutscene = false


func _on_shelburne_load_body_entered(body):
	emit_signal("shelburne_generate")
#355 -36
func generate_michael_plot():
	print(player)
	var michael_plot_file = preload("res://scenes/michael_plot.tscn")
	var michael_plot_instance = michael_plot_file.instantiate()
	michael_plot_instance.position = Vector2(355, 165)
	michael_plot_instance.player = player
	add_child(michael_plot_instance)
