using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace VariantKit
{
    /// <summary>JSON-Objekt mit fester Feldreihenfolge (git-freundlich, Spec 6.1). Werte: JObj, List&lt;object&gt;, string,
    /// double, long, bool, null. Eigener kleiner Parser/Schreiber → kein Zusatzpaket nötig (Leitprinzip „kein Spezial-Plugin“).</summary>
    public class JObj : IEnumerable<KeyValuePair<string, object>>
    {
        readonly List<KeyValuePair<string, object>> items = new List<KeyValuePair<string, object>>();

        public int Count => items.Count;
        public IEnumerable<string> Keys => items.Select(k => k.Key);
        public bool Has(string k) => items.Any(p => p.Key == k);

        public object this[string key]
        {
            get { foreach (var p in items) if (p.Key == key) return p.Value; return null; }
            set
            {
                for (int i = 0; i < items.Count; i++)
                    if (items[i].Key == key) { items[i] = new KeyValuePair<string, object>(key, value); return; }
                items.Add(new KeyValuePair<string, object>(key, value));
            }
        }

        public void Remove(string key) => items.RemoveAll(p => p.Key == key);

        /// <summary>Feld an einer bestimmten Position einfügen/verschieben (feste Reihenfolge beim Schreiben).</summary>
        public void Insert(int index, string key, object value)
        {
            Remove(key);
            items.Insert(Math.Min(index, items.Count), new KeyValuePair<string, object>(key, value));
        }

        public IEnumerator<KeyValuePair<string, object>> GetEnumerator() => items.GetEnumerator();
        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() => items.GetEnumerator();

        // ------------------------------------------------------------------ typisierte Zugriffe mit Standardwert
        public float F(string k, float def) => Json.ToF(this[k], def);
        public int I(string k, int def) => this[k] == null ? def : (int)Math.Round(Json.ToF(this[k], def));
        public string S(string k, string def) => this[k] as string ?? def;
        public bool B(string k, bool def) => this[k] is bool b ? b : def;
        public JObj O(string k) => this[k] as JObj;
        public List<object> L(string k) => this[k] as List<object>;
        public List<string> Strs(string k) => L(k)?.OfType<string>().ToList() ?? new List<string>();

        /// <summary>Unterobjekt holen, bei Bedarf anlegen.</summary>
        public JObj Obj(string k)
        {
            if (!(this[k] is JObj o)) { o = new JObj(); this[k] = o; }
            return o;
        }

        public List<object> List(string k)
        {
            if (!(this[k] is List<object> l)) { l = new List<object>(); this[k] = l; }
            return l;
        }

        public float[] Vec(string k, float[] def)
        {
            var l = L(k);
            if (l == null || l.Count != def.Length) return (float[])def.Clone();
            return l.Select((v, i) => Json.ToF(v, def[i])).ToArray();
        }

        public void SetVec(string k, float[] v) => this[k] = v.Select(x => (object)(double)x).ToList();
    }

    public static class Json
    {
        public static float ToF(object v, float def)
        {
            switch (v)
            {
                case double d: return (float)d;
                case long l: return l;
                case int i: return i;
                case float f: return f;
                case bool b: return b ? 1f : 0f;
                default: return def;
            }
        }

        // ------------------------------------------------------------------ Lesen
        public static object Parse(string text)
        {
            int i = 0;
            var v = Value(text, ref i);
            Ws(text, ref i);
            if (i < text.Length) throw new FormatException($"JSON: Zeichen nach dem Ende bei {i}");
            return v;
        }

        public static JObj ParseObj(string text) => Parse(text) as JObj ?? throw new FormatException("JSON: kein Objekt");

        static void Ws(string s, ref int i) { while (i < s.Length && char.IsWhiteSpace(s[i])) i++; }

        static object Value(string s, ref int i)
        {
            Ws(s, ref i);
            if (i >= s.Length) throw new FormatException("JSON: unerwartetes Ende");
            char c = s[i];
            if (c == '{')
            {
                var o = new JObj(); i++;
                Ws(s, ref i);
                if (s[i] == '}') { i++; return o; }
                while (true)
                {
                    Ws(s, ref i);
                    var k = Str(s, ref i);
                    Ws(s, ref i);
                    if (s[i] != ':') throw new FormatException($"JSON: ':' erwartet bei {i}");
                    i++;
                    o[k] = Value(s, ref i);
                    Ws(s, ref i);
                    if (s[i] == ',') { i++; continue; }
                    if (s[i] == '}') { i++; return o; }
                    throw new FormatException($"JSON: ',' oder '}}' erwartet bei {i}");
                }
            }
            if (c == '[')
            {
                var l = new List<object>(); i++;
                Ws(s, ref i);
                if (s[i] == ']') { i++; return l; }
                while (true)
                {
                    l.Add(Value(s, ref i));
                    Ws(s, ref i);
                    if (s[i] == ',') { i++; continue; }
                    if (s[i] == ']') { i++; return l; }
                    throw new FormatException($"JSON: ',' oder ']' erwartet bei {i}");
                }
            }
            if (c == '"') return Str(s, ref i);
            if (s.Substring(i).StartsWith("true")) { i += 4; return true; }
            if (s.Substring(i).StartsWith("false")) { i += 5; return false; }
            if (s.Substring(i).StartsWith("null")) { i += 4; return null; }
            int st = i;
            while (i < s.Length && "+-0123456789.eE".IndexOf(s[i]) >= 0) i++;
            var num = s.Substring(st, i - st);
            if (num.Length == 0) throw new FormatException($"JSON: Wert erwartet bei {st}");
            if (num.IndexOfAny(new[] { '.', 'e', 'E' }) < 0 && long.TryParse(num, NumberStyles.Integer, CultureInfo.InvariantCulture, out var lv)) return lv;
            return double.Parse(num, NumberStyles.Float, CultureInfo.InvariantCulture);
        }

        static string Str(string s, ref int i)
        {
            if (s[i] != '"') throw new FormatException($"JSON: '\"' erwartet bei {i}");
            i++;
            var sb = new StringBuilder();
            while (s[i] != '"')
            {
                if (s[i] == '\\')
                {
                    i++;
                    switch (s[i])
                    {
                        case 'n': sb.Append('\n'); break;
                        case 't': sb.Append('\t'); break;
                        case 'r': sb.Append('\r'); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'u': sb.Append((char)Convert.ToInt32(s.Substring(i + 1, 4), 16)); i += 4; break;
                        default: sb.Append(s[i]); break;
                    }
                }
                else sb.Append(s[i]);
                i++;
            }
            i++;
            return sb.ToString();
        }

        // ------------------------------------------------------------------ Schreiben (2 Leerzeichen, \n, 3 Nachkommastellen)
        public static string Write(object v)
        {
            var sb = new StringBuilder();
            W(sb, v, 0);
            sb.Append('\n');
            return sb.ToString();
        }

        static bool Simple(object v) => !(v is JObj) && !(v is List<object>);

        static void W(StringBuilder sb, object v, int ind)
        {
            switch (v)
            {
                case null: sb.Append("null"); break;
                case bool b: sb.Append(b ? "true" : "false"); break;
                case string s: Q(sb, s); break;
                case long l: sb.Append(l.ToString(CultureInfo.InvariantCulture)); break;
                case int n: sb.Append(n.ToString(CultureInfo.InvariantCulture)); break;
                case double d: Num(sb, d); break;
                case float f: Num(sb, f); break;
                case List<object> l:
                    if (l.Count == 0) { sb.Append("[]"); break; }
                    if (l.All(Simple))
                    {
                        sb.Append('[');
                        for (int k = 0; k < l.Count; k++) { if (k > 0) sb.Append(", "); W(sb, l[k], ind); }
                        sb.Append(']');
                        break;
                    }
                    sb.Append("[\n");
                    for (int k = 0; k < l.Count; k++)
                    {
                        sb.Append(' ', (ind + 1) * 2);
                        W(sb, l[k], ind + 1);
                        sb.Append(k < l.Count - 1 ? ",\n" : "\n");
                    }
                    sb.Append(' ', ind * 2).Append(']');
                    break;
                case JObj o:
                    if (o.Count == 0) { sb.Append("{}"); break; }
                    // kleine flache Objekte (z. B. Masken, Farbgruppen) in eine Zeile
                    if (o.All(p => Simple(p.Value) || (p.Value is List<object> pl && pl.All(Simple))) && o.Count <= 8 && ind > 0)
                    {
                        var line = new StringBuilder("{ ");
                        int k = 0;
                        foreach (var p in o) { if (k++ > 0) line.Append(", "); Q(line, p.Key); line.Append(": "); W(line, p.Value, ind); }
                        line.Append(" }");
                        if (line.Length + ind * 2 < 150) { sb.Append(line); break; }
                    }
                    sb.Append("{\n");
                    int c = 0;
                    foreach (var p in o)
                    {
                        sb.Append(' ', (ind + 1) * 2);
                        Q(sb, p.Key);
                        sb.Append(": ");
                        W(sb, p.Value, ind + 1);
                        sb.Append(++c < o.Count ? ",\n" : "\n");
                    }
                    sb.Append(' ', ind * 2).Append('}');
                    break;
                default: Q(sb, v.ToString()); break;
            }
        }

        static void Num(StringBuilder sb, double d)
        {
            d = Math.Round(d, 3);
            var s = d.ToString("0.0##", CultureInfo.InvariantCulture);
            sb.Append(s == "-0.0" ? "0.0" : s);
        }

        static void Q(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (var ch in s)
            {
                switch (ch)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default: sb.Append(ch); break;
                }
            }
            sb.Append('"');
        }

        // ------------------------------------------------------------------ Kopieren, Zusammenführen, Unterschied (Spec 5.4)
        public static object Clone(object v)
        {
            switch (v)
            {
                case JObj o: { var c = new JObj(); foreach (var p in o) c[p.Key] = Clone(p.Value); return c; }
                case List<object> l: return l.Select(Clone).ToList();
                default: return v;
            }
        }

        static bool IdList(object v) => v is List<object> l && l.Count > 0 && l.All(x => x is JObj o && o["id"] is string);

        /// <summary>over auf base anwenden (neues Objekt). Objekte feldweise, Listen mit „id“ je Eintrag (gleiche id =
        /// ändern, neue id = anhängen, "an": false = abschalten bleibt als Feld stehen), sonst ersetzen.</summary>
        public static object Merge(object b, object over)
        {
            if (b is JObj bo && over is JObj oo)
            {
                var r = (JObj)Clone(bo);
                foreach (var p in oo) r[p.Key] = r.Has(p.Key) ? Merge(r[p.Key], p.Value) : Clone(p.Value);
                return r;
            }
            if (b is List<object> bl && over is List<object> ol && (IdList(bl) || IdList(ol)) && ol.All(x => x is JObj))
            {
                var r = bl.Select(Clone).ToList();
                foreach (JObj e in ol)
                {
                    var id = e["id"] as string;
                    int i = id == null ? -1 : r.FindIndex(x => x is JObj xo && xo["id"] as string == id);
                    if (i >= 0) r[i] = Merge(r[i], e);
                    else r.Add(Clone(e));
                }
                return r;
            }
            return Clone(over);
        }

        public static bool Same(object a, object b)
        {
            if (a == null || b == null) return a == null && b == null;
            if ((a is double || a is long || a is float || a is int) && (b is double || b is long || b is float || b is int))
                return Math.Abs(ToF(a, 0) - ToF(b, 0)) < 5e-4;
            if (a is JObj ao && b is JObj bo)
                return ao.Count == bo.Count && ao.All(p => bo.Has(p.Key) && Same(p.Value, bo[p.Key]));
            if (a is List<object> al && b is List<object> bl)
                return al.Count == bl.Count && al.Zip(bl, Same).All(x => x);
            return a.Equals(b);
        }

        /// <summary>Nur das, was in „resolved“ von „b“ abweicht (gespeicherte Fassung = Anpassung zum Preset). null = gleich.</summary>
        public static object Diff(object resolved, object b)
        {
            if (resolved is JObj ro && b is JObj bo)
            {
                var r = new JObj();
                foreach (var p in ro)
                {
                    if (!bo.Has(p.Key)) { r[p.Key] = Clone(p.Value); continue; }
                    var d = Diff(p.Value, bo[p.Key]);
                    if (d != NoChange) r[p.Key] = d;
                }
                return r.Count == 0 ? NoChange : r;
            }
            if (resolved is List<object> rl && b is List<object> bl && (IdList(rl) || IdList(bl)))
            {
                var r = new List<object>();
                foreach (JObj e in rl.OfType<JObj>())
                {
                    var id = e["id"] as string;
                    var be = bl.OfType<JObj>().FirstOrDefault(x => x["id"] as string == id);
                    if (be == null) { r.Add(Clone(e)); continue; }
                    var d = Diff(e, be);
                    if (d is JObj dj) { dj.Insert(0, "id", id); r.Add(dj); }
                }
                foreach (JObj be in bl.OfType<JObj>())
                    if (!rl.OfType<JObj>().Any(x => x["id"] as string == be["id"] as string))
                        r.Add(new JObj { ["id"] = be["id"], ["an"] = false });
                return r.Count == 0 ? NoChange : r;
            }
            return Same(resolved, b) ? NoChange : Clone(resolved);
        }

        public static readonly object NoChange = new object();

        /// <summary>FNV-1a 32 Bit (Spec 6.2: Seed pro Eintrag = fnv1a32("&lt;seed&gt;:&lt;id&gt;")).</summary>
        public static int Fnv1a(string s)
        {
            uint h = 2166136261;
            foreach (var b in Encoding.UTF8.GetBytes(s)) { h ^= b; h *= 16777619; }
            return (int)(h & 0x7fffffff);
        }
    }
}
