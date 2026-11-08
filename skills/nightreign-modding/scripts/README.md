# SoulsFormats 小工具源码

编译（.NET Framework 4.x 的 csc，把 SoulsFormats.dll 与 System.Numerics 放同目录）：
    csc.exe //nologo //r:SoulsFormats.dll //r:System.Numerics.dll //out:flverkeep.exe flverkeep.cs
每个 exe 需‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌要同名 `.exe.config`（见 tool.exe.config.example，绑定 SoulsFormats 程序集版本）。

- flverkeep.cs：`in out --info | --cullinfo | --nocull 0,1 | --cull 3 | --empty 0,1 | --crop idx:z0:z1 | --uvskirt idx | --remap prefix_`（`-` 作为 out 表示只读‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌不写）
- flverdiag.cs：每网格 bbox（Y-up）、零权重顶点、原点附近‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌顶点
- flverbones.cs：骨名/父/平移/被引用顶点数
- flverdump.cs：FLVER → JSON（顶点、三角、权重、骨名）
