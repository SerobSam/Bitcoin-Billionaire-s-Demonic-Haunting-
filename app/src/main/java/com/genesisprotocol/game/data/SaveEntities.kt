package com.genesisprotocol.game.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "characters")
data class CharacterEntity(
    @PrimaryKey val id: String,
    val className: String,
    val accountHashrate: Long,
    val merkleRoot: String,
    val selectedOutfit: String
)

@Entity(tableName = "world_flags")
data class WorldFlagEntity(
    @PrimaryKey val key: String,
    val value: String,
    val updatedTick: Long
)

@Entity(tableName = "inventory_items")
data class InventoryItemEntity(
    @PrimaryKey val instanceId: String,
    val definitionId: String,
    val tier: String,
    val affixJson: String,
    val durability: Int
)
