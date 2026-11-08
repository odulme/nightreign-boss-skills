// Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
using System;
using System.Linq;
using SoulsFormats;
class P {
    static void Main(string[] a) {
        var f = FLVER2.Read(a[0]);
        Console.WriteLine("bones=" + f.Nodes.Count + " meshes=" + f.Meshes.Count);
        for (int mi = 0; mi < f.Meshes.Count; mi++) {
            var m = f.Meshes[mi];
            float minx = 1e9f, miny = 1e9f, minz = 1e9f, maxx = -1e9f, maxy = -1e9f, maxz = -1e9f;
            int zero = 0, nearOrigin = 0, badIdx = 0, over4 = 0;
            foreach (var v in m.Vertices) {
                var p = v.Position;
                minx = Math.Min(minx, p.X); miny = Math.Min(miny, p.Y); minz = Math.Min(minz, p.Z);
                maxx = Math.Max(maxx, p.X); maxy = Math.Max(maxy, p.Y); maxz = Math.Max(maxz, p.Z);
                float ws = v.BoneWeights[0] + v.BoneWeights[1] + v.BoneWeights[2] + v.BoneWeights[3];
                if (ws < 0.01f) zero++;
                if (Math.Abs(p.X) < 0.05f && Math.Abs(p.Y) < 0.05f && Math.Abs(p.Z) < 0.05f) nearOrigin++;
                for (int k = 0; k < 4; k++) {
                    int bi = v.BoneIndices[k];
                    if (v.BoneWeights[k] > 0 && (bi < 0 || (m.BoneIndices.Count > 0 ? bi >= m.BoneIndices.Count : bi >= f.Nodes.Count))) badIdx++;
                }
            }
            Console.WriteLine(string.Format("mesh[{0}] mat={1} verts={2} meshBones={3} bbox x {4:F2}..{5:F2} y {6:F2}..{7:F2} z {8:F2}..{9:F2} zeroW={10} nearOrigin={11} badIdx={12}",
                mi, m.MaterialIndex, m.Vertices.Count, m.BoneIndices.Count, minx, maxx, miny, maxy, minz, maxz, zero, nearOrigin, badIdx));
        }
    }
}
