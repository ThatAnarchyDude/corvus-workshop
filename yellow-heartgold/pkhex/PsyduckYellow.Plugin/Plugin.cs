// SPDX-License-Identifier: GPL-3.0-or-later
using PKHeX.Core;
using System.Windows.Forms;

namespace PsyduckYellow;

public sealed class Plugin : IPlugin
{
    public string Name => "Pokémon Psyduck Yellow";
    public int Priority => 0;
    public ISaveFileProvider SaveFileEditor { get; private set; } = null!;
    private IPKMView? viewer;
    private ToolStripMenuItem? entry;
    public void Initialize(params object[] args)
    {
        SaveFileEditor = args.OfType<ISaveFileProvider>().First();
        viewer = args.OfType<IPKMView>().FirstOrDefault();
        var menu = args.OfType<MenuStrip>().First();
        entry = new ToolStripMenuItem(Name);
        entry.Click += (_, _) => Open();
        var tools = menu.Items.OfType<ToolStripMenuItem>().FirstOrDefault(x => x.Name == "Menu_Tools");
        (tools?.DropDownItems ?? menu.Items).Add(entry);
        NotifySaveLoaded();
    }
    public void NotifySaveLoaded() { if (entry != null) entry.Enabled = SaveFileEditor.SAV is SAV4HGSS; }
    public bool TryLoadFile(string path) => false;
    private void Open()
    {
        if (SaveFileEditor.SAV is not SAV4HGSS save) return;
        if (MessageBox.Show("Use only with a backed-up Pokémon Psyduck Yellow save. Standard HeartGold saves share this format; this plugin cannot identify the hack automatically. Continue?", Name, MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        using var dialog = new Form { Text = Name + " — experimental compatibility", Width = 620, Height = 570, StartPosition = FormStartPosition.CenterParent };
        var layout = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, WrapContents = false, AutoScroll = true };
        dialog.Controls.Add(layout);
        string[] rows = Enumerable.Range(0,10).Select(i => $"PC slot {i+1}: item {ItemName(save.GetWork(0x152+2*i))}, quantity {save.GetWork(0x153+2*i)}").ToArray();
        var pokemon = viewer?.PreparePKM().Clone();
        var summary = "Native HeartGold save editing remains in PKHeX.\r\nProject PC storage (read-only):\r\n" + string.Join("\r\n",rows) +
            $"\r\nParcel state: {save.GetWork(0x16A)}\r\n\r\n" +
            (pokemon == null ? "No Pokémon editor is available." : $"Current Pokémon: species {pokemon.Species}; shiny XOR {pokemon.ShinyXor}.\r\nProject shiny status (XOR < 16): {pokemon.ShinyXor < 16}.\r\nOfficial Gen IV checks use XOR < 8.") +
            "\r\nCustom abilities, items and evolutions may fail official legality checks.\r\nThis plugin does not change PKHeX's official legality rules.";
        layout.Controls.Add(new TextBox { Text = summary, Width = 570, Height = 320, Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical });
        if (pokemon != null && viewer != null && pokemon.Species is 54 or 133 or 175)
        {
            var ability = pokemon.Species switch { 54 => 33, 133 => 107, 175 => 105, _ => 0 };
            var button = new Button { Text = "Apply project Hidden Ability to current Pokémon", Width = 560, Height = 38 };
            button.Click += (_,_) => {
                if (MessageBox.Show("Change only the current Pokémon's ability? Use PKHeX's Set command to place it in a party/box slot, then export your save. This is a project rule, not official Gen IV legality.", Name, MessageBoxButtons.YesNo) != DialogResult.Yes) return;
                pokemon.Ability = ability;
                viewer.PopulateFields(pokemon, true, true);
                MessageBox.Show("Applied to the editor. Set the Pokémon into its slot, then export the save. Verify the ability in-game.", Name);
                dialog.Close();
            };
            layout.Controls.Add(button);
        }
        dialog.ShowDialog();
    }
    private static string ItemName(ushort id) => id switch { 0 => "empty", 114 => "114 (Shiny Charm)", 121 => "121 (Friendship Charm)", _ => id.ToString() };
}
