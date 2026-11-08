// Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
using System;
using System.Linq;
using System.Collections.Generic;
using System.Numerics;
using SoulsFormats;
class P {
    // usage: flverkeep in out --info | --empty 0,1,2 --crop 5:0.72:0.87 --uvskirt 5 --remap prefix_
    static void Main(string[] a) {
        var f = FLVER2.Read(a[0]);
        Console.WriteLine("bones=" + f.Nodes.Count + " meshes=" + f.Meshes.Count + " materials=" + f.Materials.Count);
        for (int i = 2; i < a.Length; i++) {
            if (a[i] == "--cullinfo") {
                for (int mi = 0; mi < f.Meshes.Count; mi++) { var m = f.Meshes[mi]; var cs = new System.Collections.Generic.List<string>(); foreach (var fs in m.FaceSets) cs.Add(fs.CullBackfaces ? "cull" : "2side"); Console.WriteLine("mesh[" + mi + "] mat=" + f.Materials[m.MaterialIndex].Name + " facesets: " + string.Join(",", cs)); }
            } else if (a[i] == "--cull") {
                var idx = new System.Collections.Generic.HashSet<int>(); foreach (var t in a[i + 1].Split(',')) idx.Add(int.Parse(t)); i++;
                int n = 0; for (int mi = 0; mi < f.Meshes.Count; mi++) if (idx.Contains(mi)) foreach (var fs in f.Meshes[mi].FaceSets) { fs.CullBackfaces = true; n++; }
                Console.WriteLine("cull facesets=" + n);
            } else if (a[i] == "--nocull") {
                var idx = new System.Collections.Generic.HashSet<int>(); foreach (var t in a[i + 1].Split(',')) idx.Add(int.Parse(t)); i++;
                int n = 0; for (int mi = 0; mi < f.Meshes.Count; mi++) if (idx.Contains(mi)) foreach (var fs in f.Meshes[mi].FaceSets) { fs.CullBackfaces = false; n++; }
                Console.WriteLine("nocull facesets=" + n);
            } else if (a[i] == "--info") {
                for (int mi = 0; mi < f.Meshes.Count; mi++) { var m = f.Meshes[mi];
                    float u0 = 9, u1 = -9, v0 = 9, v1 = -9; foreach (var v in m.Vertices) { if (v.UVs.Count == 0) continue; var uv = v.UVs[0]; u0 = Math.Min(u0, uv.X); u1 = Math.Max(u1, uv.X); v0 = Math.Min(v0, uv.Y); v1 = Math.Max(v1, uv.Y); }
                    Console.WriteLine(string.Format("mesh[{0}] mat={1} ({2}) verts={3} facesets={4} strip={5} tris={6} uv u {7:F3}..{8:F3} v {9:F3}..{10:F3}", mi, m.MaterialIndex, f.Materials[m.MaterialIndex].Name, m.Vertices.Count, m.FaceSets.Count, m.FaceSets.Count > 0 && m.FaceSets[0].TriangleStrip, m.FaceSets.Count > 0 ? m.FaceSets[0].Indices.Count / 3 : 0, u0, u1, v0, v1)); }
            } else if (a[i] == "--empty") {
                foreach (var s in a[++i].Split(',')) { int mi = int.Parse(s); foreach (var fs in f.Meshes[mi].FaceSets) { fs.TriangleStrip = false; fs.Indices = new List<int> { 0, 0, 0 }; } Console.WriteLine("emptied mesh " + mi); }
            } else if (a[i] == "--crop") {
                var p = a[++i].Split(':'); int mi = int.Parse(p[0]); float z0 = float.Parse(p[1]), z1 = float.Parse(p[2]); var m = f.Meshes[mi];
                foreach (var fs in m.FaceSets) {
                    var tris = fs.Triangulate(false, true); var keep = new List<int>();
                    for (int t = 0; t + 2 < tris.Count; t += 3) { int i0 = tris[t], i1 = tris[t + 1], i2 = tris[t + 2]; if (i0 == i1 || i1 == i2 || i0 == i2) continue;
                        float y0 = m.Vertices[i0].Position.Y, y1 = m.Vertices[i1].Position.Y, y2 = m.Vertices[i2].Position.Y;
                        if (y0 >= z0 && y0 <= z1 && y1 >= z0 && y1 <= z1 && y2 >= z0 && y2 <= z1) { keep.Add(i0); keep.Add(i1); keep.Add(i2); } }
                    fs.TriangleStrip = false; fs.Indices = keep.Count > 0 ? keep : new List<int> { 0, 0, 0 };
                    Console.WriteLine("cropped mesh " + mi + " faceset: " + tris.Count / 3 + " -> " + keep.Count / 3 + " tris"); }
            } else if (a[i] == "--uvskirt") {
                int mi = int.Parse(a[++i]); var m = f.Meshes[mi]; int n = 0;
                // planar map (x, height) into the second pants leg strip of our atlas: RECT (0.515..0.905, 0.045..0.445), strip u 0.54..0.96, v 0.03..0.27 (RECT-normalised); FLVER v is flipped (1 - v)
                foreach (var v in m.Vertices) { float x = v.Position.X, h = v.Position.Y;
                    float ur = 0.54f + Math.Max(0f, Math.Min(1f, (x + 0.25f) / 0.50f)) * 0.42f; float vr = 0.03f + Math.Max(0f, Math.Min(1f, (h - 0.42f) / 0.61f)) * 0.24f;
                    float U = 0.515f + ur * 0.39f, V = 1f - (0.045f + vr * 0.40f);
                    for (int k = 0; k < v.UVs.Count; k++) v.UVs[k] = new Vector3(U, V, 0); n++; }
                Console.WriteLine("uv remapped mesh " + mi + " verts " + n);
            } else if (a[i] == "--remap") {
                string prefix = a[++i]; var map = new Dictionary<int, int>(); var drop = new List<int>();
                for (int k = 0; k < f.Materials.Count; k++) { var nm = f.Materials[k].Name; if (nm.StartsWith(prefix)) { string orig = nm.Substring(prefix.Length); int oi = f.Materials.FindIndex(mm => mm.Name == orig && !mm.Name.StartsWith(prefix)); if (oi < 0) oi = f.Materials.FindIndex(mm => mm.Name.Contains("body") && !mm.Name.StartsWith(prefix)); map[k] = oi; drop.Add(k); Console.WriteLine("material " + k + " " + nm + " -> " + oi + " " + f.Materials[oi].Name); } }
                foreach (var m in f.Meshes) if (map.ContainsKey(m.MaterialIndex)) m.MaterialIndex = map[m.MaterialIndex];
                // remove dropped materials (highest first) and shift indices
                foreach (var k in drop.OrderByDescending(x => x)) { f.Materials.RemoveAt(k); foreach (var m in f.Meshes) if (m.MaterialIndex > k) m.MaterialIndex--; }
            }
        }
        if (a[1] != "-") { f.Write(a[1]); Console.WriteLine("written " + a[1] + " meshes=" + f.Meshes.Count + " materials=" + f.Materials.Count); }
    }
}
