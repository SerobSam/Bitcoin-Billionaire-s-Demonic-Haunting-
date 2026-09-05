# Combat Loadout Progression

`src/loadout.py` provides the progression layer between campaign rewards and tactical combat abilities.

## Starting kit

Every new loadout begins with **Packet Burn**. The player can use it immediately in the tactical combat system.

## Unlocking abilities

The loadout currently supports three combat abilities:

| Ability | Initial state | Role |
|---|---|---|
| Packet Burn | Unlocked | Reliable digital damage |
| Salt Circle | Locked | Occult damage with corruption tradeoff |
| Cold Storage | Locked | Void damage and dead-wallet theming |

`unlock()` validates ability IDs against `src/combat.py`, so progression cannot silently create invalid combat actions. `require()` gives mission/UI code an explicit lock failure, while `available()` returns abilities in the stable data-definition order.

## Persistence

`to_dict()` and `from_dict()` provide a small engine-neutral serialization boundary. Unknown ability IDs are rejected during restore rather than being silently accepted.

The next campaign layer can award `salt_circle` or `cold_storage` from mission rewards without changing the combat resolver itself.
