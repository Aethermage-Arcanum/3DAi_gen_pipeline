using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using UnityEditor;

namespace VariantKit
{
    /// <summary>Blender-Brücke (Spec 6.3, Knopf „In Blender bauen“): startet Blender headless im Hintergrund
    /// (procedural/variantkit_blender/vk_headless.py -- bauen), liest Fortschritt/Fehler aus der Ausgabe und meldet das
    /// Ergebnis (&lt;ExportName&gt;.bedeckung.json). Unity blockiert dabei nicht.</summary>
    public class VkBlenderJob
    {
        public const string PrefKey = "VariantKit.BlenderPfad";
        public static string BlenderPath
        {
            get => EditorPrefs.GetString(PrefKey, @"D:\Blender\blender.exe");
            set => EditorPrefs.SetString(PrefKey, value);
        }

        public static string Script => Path.Combine(VkBase.PipelineRoot, "procedural", "variantkit_blender", "vk_headless.py");

        Process proc;
        readonly ConcurrentQueue<string> lines = new ConcurrentQueue<string>();
        public readonly List<string> log = new List<string>();
        public float progress;
        public string text = "startet …", error, outPath, info;
        public bool done, ok;
        public DateTime started;
        public string variantPath;

        public static VkBlenderJob Start(string variantPath, IEnumerable<string> extra = null)
        {
            var job = new VkBlenderJob { started = DateTime.Now, variantPath = variantPath };
            if (!File.Exists(BlenderPath)) { job.Fail($"Blender nicht gefunden: {BlenderPath} (Pfad im Baukasten-Fenster unter „Datei & Kennzahlen“ einstellen)"); return job; }
            if (!File.Exists(Script)) { job.Fail("Skript fehlt: " + Script); return job; }
            var args = new StringBuilder($"-b --factory-startup -P \"{Script}\" -- bauen --variante \"{variantPath}\"");
            if (extra != null) foreach (var e in extra) args.Append(' ').Append(e);
            var psi = new ProcessStartInfo(BlenderPath, args.ToString())
            {
                UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8,
                WorkingDirectory = VkBase.PipelineRoot,
            };
            try
            {
                job.proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
                job.proc.OutputDataReceived += (s, e) => { if (e.Data != null) job.lines.Enqueue(e.Data); };
                job.proc.ErrorDataReceived += (s, e) => { if (e.Data != null) job.lines.Enqueue(e.Data); };
                job.proc.Start();
                job.proc.BeginOutputReadLine();
                job.proc.BeginErrorReadLine();
            }
            catch (Exception ex) { job.Fail("Blender startet nicht: " + ex.Message); }
            return job;
        }

        void Fail(string msg) { error = msg; done = true; ok = false; text = "Fehler"; }

        /// <summary>Ausgabe abholen (aus EditorApplication.update). true = Zustand hat sich geändert.</summary>
        public bool Poll()
        {
            bool changed = false;
            while (lines.TryDequeue(out var l))
            {
                changed = true;
                log.Add(l);
                if (l.StartsWith("VK_FORTSCHRITT "))
                {
                    var parts = l.Split(new[] { ' ' }, 3);
                    if (parts.Length >= 2) float.TryParse(parts[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out progress);
                    text = parts.Length >= 3 ? parts[2] : text;
                }
                else if (l.StartsWith("VK_FERTIG ")) outPath = l.Substring(10).Trim();
                else if (l.StartsWith("VK_FEHLER ")) error = l.Substring(10).Trim();
                else if (l.StartsWith("VK_INFO ")) info = l.Substring(8).Trim();
            }
            if (!done && proc != null && proc.HasExited)
            {
                proc.WaitForExit();   // restliche Ausgabe
                while (lines.TryDequeue(out var l2)) { log.Add(l2); if (l2.StartsWith("VK_FERTIG ")) outPath = l2.Substring(10).Trim(); if (l2.StartsWith("VK_FEHLER ")) error = l2.Substring(10).Trim(); if (l2.StartsWith("VK_INFO ")) info = l2.Substring(8).Trim(); }
                done = true;
                ok = proc.ExitCode == 0 && error == null && outPath != null;
                if (!ok && error == null) error = $"Blender beendet mit Code {proc.ExitCode} (Log: {LogPath()})";
                text = ok ? "fertig" : "Fehler";
                progress = 1;
                File.WriteAllLines(LogPath(), log);
                changed = true;
            }
            return changed;
        }

        public string LogPath() => Path.Combine(VkBase.PipelineRoot, "temp", "vk2_blender_letzter_lauf.log");

        public void Cancel()
        {
            try { if (proc != null && !proc.HasExited) proc.Kill(); } catch (Exception) { }
            Fail("abgebrochen");
        }

        /// <summary>Für die Selbstprüfung: synchron warten.</summary>
        public bool Wait(int timeoutMs = 300000)
        {
            var t0 = DateTime.Now;
            while (!done)
            {
                Poll();
                if ((DateTime.Now - t0).TotalMilliseconds > timeoutMs) { Cancel(); break; }
                System.Threading.Thread.Sleep(50);
            }
            return ok;
        }
    }
}
