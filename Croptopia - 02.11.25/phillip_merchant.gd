extends Node2D

signal redbane_purchase
signal chive_purchase
signal pinecone_purchase
signal axe_purchase



@onready var redbane_sell_button = $CanvasLayer/shop_ui/GridContainer/redbane_purchase_button
@onready var chive_sell_button = $CanvasLayer/shop_ui/GridContainer/chive_purchase_button
@onready var pinecone_sell_button = $CanvasLayer/shop_ui/GridContainer/pinecone_purchase_button

@onready var ui = $CanvasLayer

@onready var music = $CanvasLayer/shop_ui/music

@onready var music_stop = $CanvasLayer/shop_ui/music.playing
@onready var music_time = $CanvasLayer/shop_ui/music.get_stream_playback()
#VERY ADCANCED SHOP CODE DONT BE FOOLED!

@onready var redbaneberry_icon = preload("res://pixil-frame-0 - 2024-01-16T123135.698.png")
@onready var chive_icon = preload("res://pixil-frame-0 - 2024-01-16T124429.661.png")
@onready var sorrel_icon = preload("res://pixil-frame-0 - 2024-01-16T170843.375.png")
@onready var pinecone_icon = preload("res://pixil-frame-0 - 2024-01-22T145636.059.png")
@onready var elderberry_icon = preload("res://assets/pixil-frame-0 - 2024-01-16T112753.850.png")
@onready var axe_icon = preload("res://assets/iron_axe.png")
@onready var building_table_icon = preload("res://assets/Item Assets/placeables/construction_table.png")

@onready var info_text = $CanvasLayer/shop_ui/info_frame/info_text
@onready var info_icon = $CanvasLayer/shop_ui/item_icon/info_icon
@onready var sell_button = $CanvasLayer/shop_ui/usd_coin
@onready var buy_all_button = $CanvasLayer/shop_ui/buy_all
@onready var buy_button = $CanvasLayer/shop_ui/buy_button
@onready var price_text = $CanvasLayer/shop_ui/item_amount

@onready var cost_text = $CanvasLayer/shop_ui/currency

@onready var demand_ui_position = $CanvasLayer/shop_ui/demand_frame/demand_ui_position
@onready var demand_ui_out_position = $CanvasLayer/shop_ui/demand_frame/demand_ui_out_position

var quantity = "Dollar"

var page_1
var page_2
var page_3
var page_4
var page_5
var selected_item

var chive
var redbane

signal baneberry_selected
signal chive_selected
signal sorrel_selected
signal elderberry_selected
signal pinecone_selected

var page_num = 0

var is_open = false

var money_count

signal invalid_purchase

var sell_mode = true

var item_amount
var money_cost = 1
var item_value

var dollar_const = 1

var item

var player
# Called when the node enters the scene tree for the first time.
func _ready():
	ui.visible = false
	$CanvasLayer/shop_ui/product_frame/economy_manager/demand_status_icon.visible = false
	$CanvasLayer/shop_ui/product_frame/economy_manager/demand_status_message.visible = false
	$CanvasLayer/shop_ui/product_frame/economy_manager/price.visible = false
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot1/shop_slot_sprite.texture = redbaneberry_icon
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot2/shop_slot_sprite.texture = chive_icon
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot3/shop_slot_sprite.texture = elderberry_icon
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot4/shop_slot_sprite.texture = pinecone_icon
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot5/shop_slot_sprite.texture = sorrel_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot6/shop_slot_sprite.texture = axe_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot7/shop_slot_sprite.texture = building_table_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot8/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot9/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot10/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot11/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot12/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot13/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot14/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot15/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot16/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot17/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot18/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot19/shop_slot_sprite.texture = chive_icon 
	$CanvasLayer/shop_ui/product_frame/GridContainer/shop_slot20/shop_slot_sprite.texture = chive_icon 
	
	if sell_mode:
		sell_button.visible = true
		buy_button.visible = false
	elif !sell_mode:
		sell_button.visible = false
		buy_button.visible = true


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
#	print("PROCESS")
#	print("Body = ", player)
	var music_timestamp
	if Input.is_action_just_pressed("n"):
		shop_open()
	if Input.is_action_just_pressed("escape"):
		shop_close()
	index()
func index():
	value_dictionary()
	portion()
	
	if sell_mode:
		sell_button.visible = true
		buy_button.visible = false
	elif !sell_mode:
		sell_button.visible = false
		buy_button.visible = true
	if selected_item == "Redbaneberry":
		if sell_mode:
			info_icon.texture = redbaneberry_icon
			info_text.text = str("Name: Red Baneberry 
								Use: Food or crafting 
								Rarity: Common")
			price_text.text = str("/ ",item_amount, " Redbaneberry")
			emit_signal("baneberry_selected")
			
			cost_text.text = str(money_cost," USD")
			
			if quantity == "1x":
				price_text.text = str("/ ",1, " Redbaneberry")
			elif quantity == "Dollar":
				price_text.text = str("/ ",item_amount, " Redbaneberry")
			elif quantity == "10x":
				price_text.text = str("/ ",10, " Redbaneberry")
			elif quantity == "100x":
				price_text.text = str("/ ",100, " Redbaneberry")
		elif !sell_mode:
			info_icon.texture = redbaneberry_icon
			info_text.text = str("Name: Red Baneberry 
								Use: Food or crafting 
								Rarity: Common")
			price_text.text = str("/ ",item_amount, " Redbaneberry")
			emit_signal("baneberry_selected")
			
			cost_text.text = str(money_cost," USD")
			
			if quantity == "1x":
				price_text.text = str("/ ",1, " Redbaneberry")
			elif quantity == "Dollar":
				price_text.text = str("/ ",item_amount, " Redbaneberry")
			elif quantity == "10x":
				price_text.text = str("/ ",10, " Redbaneberry")
			elif quantity == "100x":
				price_text.text = str("/ ",100, " Redbaneberry")
	if selected_item == "Chive":
		info_icon.texture = chive_icon
		info_text.text = str("Name: Chives
							Use: Food or crafting 
							Rarity: Common")
		price_text.text = str("/ ",item_amount, " Chives")
		
		cost_text.text = str(money_cost," USD")
		
		if quantity == "1x":
				price_text.text = str("/ ",1, " Redbaneberry")
	if selected_item == "Elderberry":
		info_icon.texture = elderberry_icon
		info_text.text = str("Name: Elderberries
							Use: Food or crafting 
							Rarity: Uncommon")
		price_text.text = str("/ ",item_amount, " Elderberry")
		
		cost_text.text = str(money_cost," USD")
		
		if quantity == "1x":
				price_text.text = str("/ ",1, " Elderberry")
		elif quantity == "Dollar":
			price_text.text = str("/ ",item_amount, " Elderberry")
		elif quantity == "10x":
			price_text.text = str("/ ",10, " Elderberry")
		elif quantity == "100x":
			price_text.text = str("/ ",100, " Elderberry")
	if selected_item == "Sorrel":
		info_icon.texture = sorrel_icon
		info_text.text = str("Name: Sorrel
							Use: Food or crafting 
							Rarity: Uncommon")
		price_text.text = str("/ ",item_amount, " Sorrel")
		
		cost_text.text = str(money_cost," USD")
		
		if quantity == "1x":
				price_text.text = str("/ ",1, " Sorrel")
		elif quantity == "Dollar":
			price_text.text = str("/ ",item_amount, " Sorrel")
		elif quantity == "10x":
			price_text.text = str("/ ",10, " Sorrel")
		elif quantity == "100x":
			price_text.text = str("/ ",100, " Sorrel")
			
			
	if selected_item == "Pinecone":
		info_icon.texture = pinecone_icon
		info_text.text = str("Name: Pinecone
							Use: Food or crafting 
							Rarity: Common")
		price_text.text = str("/ ",item_amount, " Pinecone")
		
		cost_text.text = str(money_cost," USD")
		
		if quantity == "1x":
				price_text.text = str("/ ",1, " Pinecone")
		elif quantity == "Dollar":
			price_text.text = str("/ ",item_amount, " Pinecone")
		elif quantity == "10x":
			price_text.text = str("/ ",10, " Pinecone")
		elif quantity == "100x":
			price_text.text = str("/ ",100, " Pinecone")
	if selected_item == "Iron Axe":
		info_icon.texture = axe_icon
		info_text.text = str("Name: Iron Axe
							Use: Tool
							Rarity: Epic")
		price_text.text = str("/ ",item_amount, " Pinecone")
		
		cost_text.text = str(money_cost," USD")
	if selected_item == "Construction Table":
		info_icon.texture = building_table_icon
		info_text.text = str("Name: Construction Table
							Use: Placeable
							Rarity: Common")
		price_text.text = str("/ ",item_amount, " Pinecone")
		
		cost_text.text = str(money_cost," USD")
		
	if quantity == "Dollar":
		money_cost = 1
#		item_value = item_amount
		
		item_amount = 1
		
	if !$CanvasLayer/shop_ui/quantity_container/pcs_1_quantity.button_pressed and !$CanvasLayer/shop_ui/quantity_container/pcs_10_quantity.button_pressed and !$CanvasLayer/shop_ui/quantity_container/pcs_100_quantity.button_pressed and !$CanvasLayer/shop_ui/quantity_container/dollar_quantity.button_pressed:
		quantity = "Dollar"
func shop_open():
	ui.visible = true
	music.play()
	
func shop_close():
	ui.visible = false
	music.playing = false
	
func _on_redbane_purchase_button_pressed():
	emit_signal("redbane_purchase")


func _on_chive_purchase_button_pressed():
	emit_signal("chive_purchase")


func _on_pinecone_purchase_button_pressed():
	emit_signal("pinecone_purchase")



func _on_shop_slot_1_button_pressed():
	selected_item = "Redbaneberry"
	
	index()

func _on_shop_slot_2_button_2_pressed():
	selected_item = "Chive"
	
	index()
func _on_shop_slot_3_button_pressed():
	selected_item = "Elderberry"
	
	index()
func _on_shop_slot_4_button_pressed():
	selected_item = "Pinecone"
	
	index()
func _on_shop_slot_5_button_pressed():
	selected_item = "Sorrel"
	
	index()

func _on_usd_coin_pressed():
	if selected_item == "Redbaneberry":
		emit_signal("redbane_purchase")
		print("Redbane Purchase")
	elif selected_item == "Chive":
		emit_signal("chive_purchase")
	elif selected_item == "Axe":
		emit_signal("axe_purchase")


func _on_demand_info_button_pressed():
	$CanvasLayer/shop_ui/demand_frame/ui_page_1.position = demand_ui_position.position


func _on_next_ui_page_pressed():
	page_num = page_num + 1
	if page_num == 1:
		$CanvasLayer/shop_ui/demand_frame/ui_page_1.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_2.position = demand_ui_position.position
	if page_num == 2:
		$CanvasLayer/shop_ui/demand_frame/ui_page_2.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_3.position = demand_ui_position.position
	if page_num == 3:
		$CanvasLayer/shop_ui/demand_frame/ui_page_3.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_4.position = demand_ui_position.position
	if page_num == 4:
		$CanvasLayer/shop_ui/demand_frame/ui_page_4.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_5.position = demand_ui_position.position
	if page_num == 5:
		$CanvasLayer/shop_ui/demand_frame/ui_page_5.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_6.position = demand_ui_position.position
	if page_num == 6:
		$CanvasLayer/shop_ui/demand_frame/ui_page_6.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_7.position = demand_ui_position.position
	if page_num == 7:
		$CanvasLayer/shop_ui/demand_frame/ui_page_7.position = demand_ui_out_position.position
		$CanvasLayer/shop_ui/demand_frame/ui_page_8.position = demand_ui_position.position
	if page_num == 8:
		$CanvasLayer/shop_ui/demand_frame/ui_page_8.position = demand_ui_out_position.position
		page_num = 0


func _on_shop_slot_6_button_pressed():
	selected_item = "Iron Axe"
	
	index()
func _on_phillip_merchant_chive_purchase():
	if chive > 10:
		emit_signal("chive_purchase")
		money_count = money_count + 1
		chive = chive - 10
		
	else:
		emit_signal("invalid_purchase")


func _on_phillip_merchant_redbane_purchase():
	if redbane > 10:
		emit_signal("redbane_purchase")
		money_count = money_count + 1
		redbane = redbane - 10
		emit_signal("update_slot")
	else:
		emit_signal("invalid_purchase")
		
func _on_phillip_merchant_axe_purchase():
	var player = null
	player.can_move = false
	player.alt_move_set = true
	player.wields_axe = true
	var item = preload("res://scenes/items/iron_axe.tres")
	player.collect(item)
#	$Node2D/objects/player/AnimatedSprite2D.play("wield_walk_s")
	print("WIELD THE TOOL!!!!!!!!")


func _on_shop_slot_7_button_pressed():
	selected_item = "Construction Table"
	
	index()

func _on_sell_buy_toggle_button_toggled(button_pressed):
	if button_pressed:
		sell_mode = false
	elif !button_pressed:
		sell_mode = true
	
	index()

func _on_buy_all_pressed():
	if selected_item == "example":
		pass

func _on_dollar_quantity_pressed():
	quantity = "Dollar"
	$CanvasLayer/shop_ui/quantity_container/pcs_1_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_10_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_100_quantity.button_pressed = false
	
	index()

func _on_pcs_1_quantity_pressed():
	quantity = "1x"
	$CanvasLayer/shop_ui/quantity_container/dollar_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_10_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_100_quantity.button_pressed = false
	
	index()
	portion()
	

func _on_pcs_10_quantity_pressed():
	quantity = "10x"
	$CanvasLayer/shop_ui/quantity_container/dollar_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_1_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_100_quantity.button_pressed = false
	
	index()
	portion()
	

func _on_pcs_100_quantity_pressed():
	quantity = "100x"
	$CanvasLayer/shop_ui/quantity_container/dollar_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_10_quantity.button_pressed = false
	$CanvasLayer/shop_ui/quantity_container/pcs_1_quantity.button_pressed = false
	
	index()
	portion()
	
func portion():
	if quantity == "1x":
#		print("AMOUNT",dollar_const - item_amount / 10.5)
		var calc
		calc = 1.0 / (item_amount)
		money_cost = float(str( calc ).pad_decimals(2))
		
		#MAYBE dollar_const / item_amount * 10.5
		
	if quantity == "10x":
		var calc
		calc = 1.0 / (item_amount) * 10
		money_cost = float(str( calc ).pad_decimals(2))
		
	if quantity == "100x":
		var calc
		calc = 1.0 / (item_amount) * 100
		money_cost = float(str( calc ).pad_decimals(2))
		
func value_dictionary():
	if sell_mode:
		var redbane_value = 8
		var chive_value = 8
		var elderberry_value = 4
		var sorrel_value = 6
		var pinecone_value = 12
		
		if selected_item == "Redbaneberry":
			item_amount = redbane_value
		if selected_item == "Chive":
			item_amount = chive_value
		if selected_item == "Elderberry":
			item_amount = elderberry_value
		if selected_item == "Sorrel":
			item_amount = sorrel_value
		if selected_item == "Pinecone":
			item_amount = pinecone_value
		if selected_item == "Iron Axe":
			item_amount = redbane_value
		if selected_item == "Construction Table":
			item_amount = redbane_value
	if !sell_mode:
		pass
		
	var redbane_usd = 8
	var chive_usd = 8
	var elderberry_usd = 4
	var sorrel_usd = 6
	var pinecone_usd = 12


func _on_player_detection_body_entered(body):
	player = body
	
	print("Body = ", player)


func _on_buy_button_pressed():
	if selected_item == "Construction Table":
		item = preload("res://inventory/items/construction_table.tres")
		player.collect(item)
func trigger():
	print("PHILLIP TRIGGER")
