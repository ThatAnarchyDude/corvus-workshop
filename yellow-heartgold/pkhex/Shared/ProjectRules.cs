// SPDX-License-Identifier: GPL-3.0-or-later
using PKHeX.Core;
namespace PsyduckYellow;

/// <summary>Project-only edits. Use after the user explicitly selects this save profile.</summary>
public static class ProjectRules
{
    public const int ShinyThreshold = 16;
    public const int PCStacks = 10;
    public static bool IsProjectShiny(PKM pokemon) => pokemon.ShinyXor < ShinyThreshold;
    public static int HiddenAbility(ushort species) => species switch {
        54 or 55 => 33, 133 => 107, 134 => 93, 135 => 95, 136 => 62,
        197 => 39, 470 => 34, 471 => 115, 175 or 176 or 468 => 105,
        _ => 0 // Espeon's Magic Bounce is unavailable in Gen IV.
    };
    public static string AbilityName(int id) => id switch {
        33 => "Swift Swim", 107 => "Anticipation", 93 => "Hydration", 95 => "Quick Feet",
        62 => "Guts", 39 => "Inner Focus", 34 => "Chlorophyll", 115 => "Ice Body",
        105 => "Super Luck", _ => "Unsupported"
    };
    public static string ItemName(ushort id) => id switch {
        0 => "Empty", 114 => "Shiny Charm", 121 => "Friendship Charm", _ => $"Item {id}"
    };
    public static PKM ApplyHiddenAbility(SAV4HGSS save, int slot)
    {
        if ((uint)slot >= save.PartyCount) throw new ArgumentOutOfRangeException(nameof(slot));
        var pokemon = save.GetPartySlotAtIndex(slot).Clone();
        int ability = HiddenAbility(pokemon.Species);
        if (pokemon.IsEgg || ability == 0) throw new InvalidOperationException("No supported project Hidden Ability for this party member.");
        pokemon.Ability = ability;
        // Direct save-slot update avoids normal PKHeX Gen IV dropdown normalization.
        save.SetPartySlotAtIndex(pokemon, slot, EntityImportSettings.None);
        return save.GetPartySlotAtIndex(slot);
    }
    public static (ushort Item, ushort Quantity) GetPCStack(SAV4HGSS save, int slot)
    {
        ValidatePCSlot(slot);
        return (save.GetWork(0x152+2*slot), save.GetWork(0x153+2*slot));
    }
    public static void SetPCStack(SAV4HGSS save, int slot, int item, int quantity)
    {
        ValidatePCSlot(slot);
        if (save.GetWork(0x166) != 1) throw new InvalidOperationException("Open the player's PC in-game first to initialize storage.");
        if (item < 0 || item > save.MaxItemID || quantity < 0 || quantity > 999 || (item==0)!=(quantity==0))
            throw new ArgumentException("Use an existing Gen IV item and quantity 1–999, or item 0/quantity 0 for an empty stack.");
        // Key items must not duplicate across storage; existing game PC deposits do not accept them.
        if ((item is 114 or 121) && quantity > 1) throw new ArgumentException("Project charms must have quantity one.");
        for (int i=0;i<PCStacks;i++)
            if (i!=slot && item!=0 && GetPCStack(save,i).Item==item && GetPCStack(save,i).Quantity!=0)
                throw new ArgumentException("This item already has a PC stack. Edit its existing stack instead.");
        save.SetWork(0x152+2*slot, (ushort)item);
        save.SetWork(0x153+2*slot, (ushort)quantity);
        save.State.Edited = true;
    }
    private static void ValidatePCSlot(int slot)
    {
        if ((uint)slot >= PCStacks) throw new ArgumentOutOfRangeException(nameof(slot));
    }
}
