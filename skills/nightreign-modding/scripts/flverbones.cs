// Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
using System;
using System.Linq;
using System.Collections.Generic;
using SoulsFormats;
class P {
    static void Main(string[] a) {
        var f = FLVER2.Read(a[0]);
        bool all = a.Length > 1 && a[1] == "--all";
        Console.WriteLine("file=" + a[0] + " bones=" + f.Nodes.Count + " meshes=" + f.Meshes.Count);
        // which bones are actually used by vertices
        var used = new Dictionary<int, int>();
        foreach (var m in f.Meshes) foreach (var v in m.Vertices) for (int k = 0; k < 4; k++) if (v.BoneWeights[k] > 0.01f) {
            int bi = v.BoneIndices[k]; if (m.BoneIndices.Count > 0 && bi >= 0 && bi < m.BoneIndices.Count) bi = m.BoneIndices[bi];
            if (bi >= 0 && bi < f.Nodes.Count) { int c; used.TryGetValue(bi, out c); used[bi] = c + 1; }
        }
        for (int i = 0; i < f.Nodes.Count; i++) {
            var n = f.Nodes[i]; bool cloth = n.Name.Contains("Cloth");
            if (!all && !cloth) continue;
            string parent = n.ParentIndex >= 0 ? f.Nodes[n.ParentIndex].Name : "-";
            int c; used.TryGetValue(i, out c);
            Console.WriteLine(string.Format("{0}\t{1}\tparent={2}\tt=({3:F3},{4:F3},{5:F3})\tused={6}", i, n.Name, parent, n.Translation.X, n.Translation.Y, n.Translation.Z, c));
        }
    }
}
