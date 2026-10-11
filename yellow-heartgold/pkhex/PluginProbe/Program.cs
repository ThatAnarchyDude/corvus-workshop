// SPDX-License-Identifier: GPL-3.0-or-later
using System.Text.Json;
using PKHeX.Core;
using PsyduckYellow;
if (args.Length!=2) throw new ArgumentException("Input copied save, private output directory required.");
var source=(SAV4HGSS)(SaveUtil.GetSaveFile(File.ReadAllBytes(args[0]),args[0]) ?? throw new InvalidDataException());
var output=Path.GetFullPath(args[1]); Directory.CreateDirectory(output);
var results=new List<object>();
foreach (ushort species in new ushort[]{54,55,133,134,135,136,197,470,471,175,176,468})
{
    var save=(SAV4HGSS)source.Clone();
    var fixture=save.GetPartySlotAtIndex(0);
    fixture.Species=species;
    fixture.Gender=species==133 ? (byte)1 : (byte)0;
    // Project-only shiny XOR 12: shiny in the hack, nonshiny under official Gen IV rules.
    uint low=fixture.PID & 0xffff;
    fixture.PID=low | ((uint)(fixture.TID16 ^ fixture.SID16 ^ low ^ 12)<<16);
    fixture.RefreshChecksum(); save.SetPartySlotAtIndex(fixture,0,EntityImportSettings.None);
    var before=save.GetPartySlotAtIndex(0).Data.ToArray();
    var vars=save.General.Slice(0xDE4,1100).ToArray();
    var dex=save.General.Slice(0x12B8,0x338).ToArray();
    var oldNature=fixture.Nature; var oldGender=fixture.Gender;
    var changed=ProjectRules.ApplyHiddenAbility(save,0);
    var bytes=save.Write().ToArray(); var reopened=(SAV4HGSS)(SaveUtil.GetSaveFile(bytes)??throw new InvalidDataException());
    var mon=reopened.GetPartySlotAtIndex(0);
    Check(reopened.ChecksumsValid && mon.ChecksumValid, "Checksums");
    Check(mon.Ability==ProjectRules.HiddenAbility(species), "Ability lost");
    Check(mon.ShinyXor==12 && ProjectRules.IsProjectShiny(mon) && !mon.IsShiny, "Shiny mismatch");
    Check(mon.PID==fixture.PID && mon.Gender==oldGender && mon.Nature==oldNature, "Personality/gender changed");
    Check(vars.SequenceEqual(reopened.General.Slice(0xDE4,1100).ToArray()), "Quest/PC flags changed");
    Check(dex.SequenceEqual(reopened.General.Slice(0x12B8,0x338).ToArray()), "Dex changed");
    // Ability byte and checksum are the only permitted changes to the original party member.
    var after=mon.Data.ToArray();
    Check(before.Where((_,i)=>i is not 6 and not 7 and not 0x15).SequenceEqual(after.Where((_,i)=>i is not 6 and not 7 and not 0x15)), "Unrelated Pokémon fields changed");
    File.WriteAllBytes(Path.Combine(output,$"species-{species}.dsv"),bytes);
    results.Add(new {species,mon.Ability,mon.ShinyXor,mon.Gender,mon.PID,checksum=mon.ChecksumValid});
}
// Both shiny thresholds and nonsupported species/slot errors are checked independently.
foreach (int xor in new[]{0,7,8,15,16,65535})
{
    var p=source.GetPartySlotAtIndex(0); uint low=p.PID&0xffff;
    p.PID=low | ((uint)(p.TID16^p.SID16^low^xor)<<16);
    Check(ProjectRules.IsProjectShiny(p)==(xor<16),"Shiny boundary");
}
Check(ProjectRules.HiddenAbility(196)==0 && ProjectRules.HiddenAbility(25)==0,"Unsupported ability");
var pc=(SAV4HGSS)source.Clone(); pc.SetWork(0x166,1);
int slot=Enumerable.Range(0,10).First(i=>ProjectRules.GetPCStack(pc,i).Item==0);
var oldVars=pc.General.Slice(0xDE4,1100).ToArray();
ProjectRules.SetPCStack(pc,slot,4,25); // Ordinary Poké Balls.
var pcBytes=pc.Write().ToArray(); var pcReopen=(SAV4HGSS)(SaveUtil.GetSaveFile(pcBytes)??throw new InvalidDataException());
Check(ProjectRules.GetPCStack(pcReopen,slot)==((ushort)4,(ushort)25),"PC stack export");
var newVars=pcReopen.General.Slice(0xDE4,1100).ToArray();
for(int i=0;i<1100;i++)if(i<2*(0x152+2*slot)||i>=2*(0x152+2*slot)+4)Check(oldVars[i]==newVars[i],"Other quest variable changed");
ExpectFailure(()=>ProjectRules.SetPCStack(pc,slot,4,1000));
ExpectFailure(()=>ProjectRules.SetPCStack(pc,slot,0,1));
ExpectFailure(()=>ProjectRules.SetPCStack(pc,slot,114,2));
ExpectFailure(()=>ProjectRules.SetPCStack(pc,10,4,1));
ExpectFailure(()=>ProjectRules.ApplyHiddenAbility(pc,6));
var uninit=(SAV4HGSS)source.Clone();uninit.SetWork(0x166,0);
ExpectFailure(()=>ProjectRules.SetPCStack(uninit,slot,4,1));
File.WriteAllBytes(Path.Combine(output,"pc-edit.dsv"),pcBytes);
var report=new {hiddenAbilityRoundTrips=results,shinyBoundaries="passed",unrelatedDataPreserved=true,pcStorage="passed",invalidEdits="rejected",nativeReload="pending",windowsUI="not tested on Linux"};
var json=JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true});
File.WriteAllText(Path.Combine(output,"plugin-report.json"),json+"\n");Console.WriteLine(json);
static void Check(bool condition,string message){if(!condition)throw new InvalidDataException(message);}
static void ExpectFailure(Action action){try{action();}catch(ArgumentException){return;}catch(InvalidOperationException){return;}throw new InvalidDataException("Invalid edit was accepted");}
