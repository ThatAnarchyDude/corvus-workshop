// SPDX-License-Identifier: GPL-3.0-or-later
using PKHeX.Core;
using PsyduckYellow;
using System.Reflection;
using System.Windows.Forms;
internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();
        var save = new SAV4HGSS { Version=GameVersion.HG };
        var eevee = new PK4 { Species=133, Gender=1, Ability=50, PID=0x12341234, ID32=12 };
        save.SetPartySlotAtIndex(eevee,0,EntityImportSettings.None);
        save.SetPartySlotAtIndex(new PK4 { Species=25, Ability=9 },1,EntityImportSettings.None);
        save.SetWork(0x166,1);
        var provider=new Provider { SAV=save };
        using var menu=new MenuStrip();
        var tools=new ToolStripMenuItem("Tools") { Name="Menu_Tools" };menu.Items.Add(tools);
        IPlugin plugin=new Plugin();plugin.Initialize(provider,menu);
        Check(tools.DropDownItems.Count==1,"Tools menu entry missing");
        Check(tools.DropDownItems[0].Enabled,"HGSS entry disabled");
        Check(!plugin.TryLoadFile("unrelated-file"),"Intercepted unrelated file");
        var creator=typeof(Plugin).GetMethod("CreateDialog",BindingFlags.NonPublic|BindingFlags.Instance)??throw new InvalidOperationException();
        using var dialog=(Form)(creator.Invoke(plugin,[save])??throw new InvalidOperationException());
        dialog.CreateControl();
        var controls=Descendants(dialog).ToArray();
        var party=controls.OfType<ComboBox>().Single();
        Check(party.Items.Count==2 && party.SelectedIndex==0,"Party selection missing");
        var ability=controls.OfType<Button>().Single(b=>b.Text.Contains("Anticipation"));
        Check(ability.Enabled,"Supported Hidden Ability disabled");
        var summary=controls.OfType<TextBox>().Single();
        Check(summary.Text.Contains("Project shiny: True"),"Project shiny display lost");
        party.SelectedIndex=1;
        Check(!ability.Enabled,"Unsupported ability enabled");
        party.SelectedIndex=0;
        Check(ability.Enabled,"Supported party reselect failed");
        var applyPC=controls.OfType<Button>().Single(b=>b.Text=="Apply PC stack edit");
        Check(applyPC.Enabled,"Initialized PC editor disabled");
        save.SetWork(0x166,0);
        using var uninitialized=(Form)creator.Invoke(plugin,[save])!;
        Check(!Descendants(uninitialized).OfType<Button>().Single(b=>b.Text=="Apply PC stack edit").Enabled,"Uninitialized PC edits enabled");
        provider.SAV=new SAV4DP();plugin.NotifySaveLoaded();
        Check(!tools.DropDownItems[0].Enabled,"Plugin enabled for a non-HGSS save");
        provider.SAV=save;plugin.NotifySaveLoaded();Check(tools.DropDownItems[0].Enabled,"Reload HGSS failed");
        Console.WriteLine("Windows plugin discovery, initialization, form construction, shiny display, party selection and PC gate: PASS");
    }
    private static IEnumerable<Control> Descendants(Control parent)
    {
        foreach(Control child in parent.Controls){yield return child;foreach(var nested in Descendants(child))yield return nested;}
    }
    private static void Check(bool condition,string message){if(!condition)throw new InvalidOperationException(message);}
    private sealed class Provider:ISaveFileProvider
    {
        public SaveFile SAV {get;set;}=null!;
        public int CurrentBox=>0;
        public void ReloadSlots() { }
    }
}
