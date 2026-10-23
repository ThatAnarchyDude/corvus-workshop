// SPDX-License-Identifier: GPL-3.0-or-later
using PKHeX.Core;
using System.Windows.Forms;
namespace PsyduckYellow;

public sealed class Plugin : IPlugin
{
    public string Name => "Pokémon Psyduck Yellow";
    public int Priority => 0;
    public ISaveFileProvider SaveFileEditor { get; private set; } = null!;
    private ToolStripMenuItem? entry;
    public void Initialize(params object[] args)
    {
        SaveFileEditor = args.OfType<ISaveFileProvider>().First();
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
        if (MessageBox.Show("Use with a backup of a Pokémon Psyduck Yellow save. Ordinary HeartGold saves have the same format. Use the project profile?", Name, MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        using var dialog = CreateDialog(save);
        dialog.ShowDialog();
    }
    private Form CreateDialog(SAV4HGSS save)
    {
        var dialog = new Form { Text = Name + " — experimental", Width = 650, Height = 730, StartPosition = FormStartPosition.CenterParent };
        var layout = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, WrapContents = false, AutoScroll = true };
        dialog.Controls.Add(layout);
        var summary = new TextBox { Width = 600, Height = 280, Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical };
        layout.Controls.Add(summary);
        var party = new ComboBox { Width = 600, DropDownStyle = ComboBoxStyle.DropDownList };
        for (int i=0;i<save.PartyCount;i++) { var p=save.GetPartySlotAtIndex(i); party.Items.Add($"Party {i+1}: {p.Nickname} (species {p.Species})"); }
        layout.Controls.Add(party);
        var hidden = new Button { Width = 600, Height = 38 };
        layout.Controls.Add(hidden);
        void Refresh()
        {
            var rows = Enumerable.Range(0,10).Select(i => { var stack=ProjectRules.GetPCStack(save,i); return $"PC {i+1}: {ProjectRules.ItemName(stack.Item)} [{stack.Item}] x{stack.Quantity}"; });
            summary.Text="Project PC storage:\r\n"+string.Join("\r\n",rows)+$"\r\nParcel state: {save.GetWork(0x16A)}\r\n";
            hidden.Enabled=false;hidden.Text="No supported Hidden Ability for this party member";
            if (party.SelectedIndex >= 0)
            {
                var p=save.GetPartySlotAtIndex(party.SelectedIndex); int ability=ProjectRules.HiddenAbility(p.Species);
                summary.AppendText($"\r\nSelected party member: {p.Nickname}; ability {p.Ability}\r\nProject shiny: {ProjectRules.IsProjectShiny(p)}; shiny XOR: {p.ShinyXor}\r\nGender: {p.Gender}; friendship: {p.CurrentFriendship}");
                hidden.Enabled=ability!=0&&!p.IsEgg;
                if(hidden.Enabled) hidden.Text=$"Apply {ProjectRules.AbilityName(ability)} to party slot {party.SelectedIndex+1}";
            }
        }
        party.SelectedIndexChanged += (_,_) => Refresh();
        hidden.Click += (_,_) => {
            if (MessageBox.Show("Apply this ability to the selected saved party slot? Personality, gender, IVs and shiny status are preserved. Export the save afterward. Standard PKHeX editing can replace custom abilities, so apply this last.", Name, MessageBoxButtons.YesNo) != DialogResult.Yes) return;
            try { ProjectRules.ApplyHiddenAbility(save,party.SelectedIndex); SaveFileEditor.ReloadSlots(); Refresh(); }
            catch(Exception ex) { MessageBox.Show(ex.Message,Name); }
        };
        layout.Controls.Add(new Label { Text="Edit one player PC stack (requires initialized in-game storage):", Width=600, Height=30 });
        var row=new FlowLayoutPanel { Width=610, Height=40 };
        var stackSlot=new NumericUpDown { Minimum=1, Maximum=10, Width=65 };
        var item=new NumericUpDown { Minimum=0, Maximum=save.MaxItemID, Width=100 };
        var quantity=new NumericUpDown { Minimum=0, Maximum=999, Width=100 };
        row.Controls.Add(new Label { Text="Slot",Width=35 });row.Controls.Add(stackSlot);
        row.Controls.Add(new Label { Text="Item ID",Width=55 });row.Controls.Add(item);
        row.Controls.Add(new Label { Text="Count",Width=45 });row.Controls.Add(quantity);
        layout.Controls.Add(row);
        void LoadStack() { var s=ProjectRules.GetPCStack(save,(int)stackSlot.Value-1);item.Value=Math.Min(item.Maximum,s.Item);quantity.Value=Math.Min(quantity.Maximum,s.Quantity); }
        stackSlot.ValueChanged+=(_,_)=>LoadStack();
        var applyPC=new Button { Text="Apply PC stack edit",Width=600,Height=38,Enabled=save.GetWork(0x166)==1 };
        layout.Controls.Add(applyPC);
        applyPC.Click+=(_,_)=>{
            if(MessageBox.Show("Replace this player PC stack with the entered item/count? Export your save afterward.",Name,MessageBoxButtons.YesNo)!=DialogResult.Yes)return;
            try { ProjectRules.SetPCStack(save,(int)stackSlot.Value-1,(int)item.Value,(int)quantity.Value);Refresh(); }
            catch(Exception ex) { MessageBox.Show(ex.Message,Name); }
        };
        layout.Controls.Add(new Label { Width=600,Height=110,Text="Changes affect PKHeX's loaded save. Use File → Export SAV afterward.\r\nApply custom abilities after other Pokémon edits. Do not Set a stale Pokémon from the normal editor over this slot.\r\nProject shiny status uses XOR < 16; stock icons/checks use XOR < 8.\r\nOfficial legality rules are unchanged. Windows UI testing is pending." });
        if (party.Items.Count>0)party.SelectedIndex=0;else Refresh();LoadStack();
        return dialog;
    }
}
