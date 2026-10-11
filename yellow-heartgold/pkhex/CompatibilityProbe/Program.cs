using System.Security.Cryptography;
using System.Text.Json;
using PKHeX.Core;

if (args.Length != 2) throw new ArgumentException("Provide an input battery save and a private output directory.");
var path = Path.GetFullPath(args[0]);
var directory = Path.GetFullPath(args[1]);
Directory.CreateDirectory(directory);
var source = File.ReadAllBytes(path);
var save = SaveUtil.GetSaveFile(source, path) as SAV4HGSS ?? throw new InvalidDataException("Not recognized as HGSS.");
Require(save.ChecksumsValid, "Input checksums invalid");
var varsFlags = save.General.Slice(0xDE4, 1100).ToArray();
var dex = save.General.Slice(0x12B8, 0x338).ToArray();
var party = save.PartyData.Select(p => p.Data.ToArray()).ToArray();
var noEdit = (SAV4HGSS)save.Clone();
var bytes = noEdit.Write().ToArray();
var reopened = SaveUtil.GetSaveFile(bytes) as SAV4HGSS ?? throw new InvalidDataException("Round trip unrecognized");
Require(reopened.ChecksumsValid, "Round-trip checksums invalid");
Require(source.Length == bytes.Length, "Emulator footer/length changed");
Require(varsFlags.SequenceEqual(reopened.General.Slice(0xDE4, 1100).ToArray()), "Quest/PC variables changed");
Require(dex.SequenceEqual(reopened.General.Slice(0x12B8, 0x338).ToArray()), "Dex changed");
for (var i = 0; i < party.Length; i++) Require(party[i].SequenceEqual(reopened.GetPartySlotAtIndex(i).Data.ToArray()), "Party changed");
File.WriteAllBytes(Path.Combine(directory, "roundtrip.dsv"), bytes);
var edited = (SAV4HGSS)save.Clone();
var mon = edited.GetPartySlotAtIndex(0);
var before = mon.IV_HP;
mon.IV_HP = (before + 1) % 32;
edited.SetPartySlotAtIndex(mon, 0, EntityImportSettings.None);
edited.Money = save.Money == 999999 ? 999998 : save.Money + 1;
var editedBytes = edited.Write().ToArray();
var editedReopen = SaveUtil.GetSaveFile(editedBytes) as SAV4HGSS ?? throw new InvalidDataException("Edited save unrecognized");
Require(editedReopen.ChecksumsValid, "Edited checksums invalid");
Require(editedReopen.GetPartySlotAtIndex(0).IV_HP == (before + 1) % 32, "IV edit lost");
Require(editedReopen.Money == edited.Money, "Money edit lost");
Require(varsFlags.SequenceEqual(editedReopen.General.Slice(0xDE4, 1100).ToArray()), "Edited save lost quest/PC variables");
File.WriteAllBytes(Path.Combine(directory, "edited.dsv"), editedBytes);
var report = new {
    recognized = save.GetType().Name, version = save.Version.ToString(), checksums = save.ChecksumsValid,
    inputBytes = source.Length, inputSHA256 = Convert.ToHexString(SHA256.HashData(source)).ToLowerInvariant(),
    coreVersion = typeof(SaveFile).Assembly.GetName().Version?.ToString(),
    party = save.PartyData.Select(p => new { p.Species, p.CurrentLevel, p.Ability, p.Gender, p.IsShiny, p.ShinyXor, p.IV_HP, p.IV_ATK, p.IV_DEF, p.IV_SPA, p.IV_SPD, p.IV_SPE, p.CurrentFriendship }).ToArray(),
    noEditRoundTrip = "passed", questPCAndFlagsPreserved = true, dexPreserved = true,
    explicitEdits = new { oldHPIV = before, newHPIV = editedReopen.GetPartySlotAtIndex(0).IV_HP, oldMoney = save.Money, newMoney = editedReopen.Money },
    emulatorReload = "pending; C# reparse alone does not establish in-game compatibility"
};
var json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
File.WriteAllText(Path.Combine(directory, "report.json"), json + "\n");
Console.WriteLine(json);
static void Require(bool value, string message) { if (!value) throw new InvalidDataException(message); }
