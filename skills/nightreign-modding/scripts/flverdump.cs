// Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
using System;
using System.IO;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;
using SoulsFormats;
class P {
    // flverdump in.flver out.json : bones (name,parent,translation,rotation,scale) + meshes (material, verts: pos, normal, uv0, bones(global idx), weights, tris)
    static string F(float v) { return v.ToString("R", CultureInfo.InvariantCulture); }
    static void Main(string[] a) {
        var f = FLVER2.Read(a[0]); var sb = new StringBuilder(); sb.Append("{\"bones\":[");
        for (int i = 0; i < f.Nodes.Count; i++) { var n = f.Nodes[i]; if (i > 0) sb.Append(",");
            sb.Append("{\"name\":\"" + n.Name.Replace("\\", "/").Replace("\"", "'") + "\",\"parent\":" + n.ParentIndex + ",\"t\":[" + F(n.Translation.X) + "," + F(n.Translation.Y) + "," + F(n.Translation.Z) + "],\"r\":[" + F(n.Rotation.X) + "," + F(n.Rotation.Y) + "," + F(n.Rotation.Z) + "],\"s\":[" + F(n.Scale.X) + "," + F(n.Scale.Y) + "," + F(n.Scale.Z) + "]}"); }
        sb.Append("],\"materials\":[" + string.Join(",", f.Materials.Select(m => "\"" + m.Name.Replace("\"", "'") + "\"")) + "],\"meshes\":[");
        for (int mi = 0; mi < f.Meshes.Count; mi++) { var m = f.Meshes[mi]; if (mi > 0) sb.Append(",");
            sb.Append("{\"material\":" + m.MaterialIndex + ",\"pos\":[");
            bool first = true;
            foreach (var v in m.Vertices) { if (!first) sb.Append(","); first = false; sb.Append(F(v.Position.X) + "," + F(v.Position.Y) + "," + F(v.Position.Z)); }
            sb.Append("],\"uv\":["); first = true;
            foreach (var v in m.Vertices) { if (!first) sb.Append(","); first = false; if (v.UVs.Count > 0) sb.Append(F(v.UVs[0].X) + "," + F(v.UVs[0].Y)); else sb.Append("0,0"); }
            sb.Append("],\"bw\":["); first = true;
            foreach (var v in m.Vertices) { for (int k = 0; k < 4; k++) { if (!first) sb.Append(","); first = false; int bi = v.BoneIndices[k]; if (m.BoneIndices.Count > 0 && bi >= 0 && bi < m.BoneIndices.Count) bi = m.BoneIndices[bi]; sb.Append(bi + "," + F(v.BoneWeights[k])); } }
            sb.Append("],\"tris\":["); first = true;
            if (m.FaceSets.Count > 0) { var tris = m.FaceSets[0].Triangulate(false, false); foreach (var t in tris) { if (!first) sb.Append(","); first = false; sb.Append(t); } }
            sb.Append("]}"); }
        sb.Append("]}"); File.WriteAllText(a[1], sb.ToString()); Console.WriteLine("dumped " + a[0] + " meshes=" + f.Meshes.Count + " bones=" + f.Nodes.Count);
    }
}
