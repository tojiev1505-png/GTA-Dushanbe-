using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Xml;
using CodeWalker.GameFiles;

internal static class Program
{
    private const string ExpectedRscMagic = "RSC7";

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 2)
            {
                Console.Error.WriteLine("Usage: CitySliceConverter <city-export-folder> <output-folder>");
                return 2;
            }

            var inputDir = Path.GetFullPath(args[0]);
            var outputDir = Path.GetFullPath(args[1]);
            if (!Directory.Exists(inputDir))
                throw new DirectoryNotFoundException($"CWXML input directory not found: {inputDir}");

            Directory.CreateDirectory(outputDir);
            var streamDir = Path.Combine(outputDir, "stream");
            Directory.CreateDirectory(streamDir);

            // This build is explicitly for GTA V Legacy (GEN8), not Enhanced / GEN9.
            RpfManager.IsGen9 = false;

            var ydrXmlFiles = Directory.GetFiles(inputDir, "*.ydr.xml", SearchOption.TopDirectoryOnly)
                .OrderBy(p => p, StringComparer.OrdinalIgnoreCase)
                .ToArray();
            var ytypXml = Path.Combine(inputDir, "dushanbe_istiklol.ytyp.xml");
            var ymapXml = Path.Combine(inputDir, "dushanbe_istiklol.ymap.xml");

            if (ydrXmlFiles.Length != 7)
                throw new InvalidDataException($"Expected 7 YDR CWXML files; found {ydrXmlFiles.Length}");
            if (!File.Exists(ytypXml))
                throw new FileNotFoundException("Missing YTYP CWXML", ytypXml);
            if (!File.Exists(ymapXml))
                throw new FileNotFoundException("Missing YMAP CWXML", ymapXml);

            var ydrResults = new List<NativeAssetRecord>();
            foreach (var ydrXml in ydrXmlFiles)
            {
                var stem = Path.GetFileName(ydrXml);
                const string suffix = ".ydr.xml";
                if (!stem.EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException($"Unexpected YDR CWXML filename: {stem}");

                var assetName = stem[..^suffix.Length];
                var textureFolder = Path.Combine(inputDir, assetName);
                var document = LoadXml(ydrXml);
                RequireRoot(document, "Drawable", ydrXml);

                var binary = XmlMeta.GetData(document, MetaFormat.Ydr, textureFolder);
                if (binary is null || binary.Length == 0)
                    throw new InvalidDataException($"CodeWalker did not convert {stem} to binary YDR data");

                ValidateRscHeader(binary, stem);
                var parsed = new YdrFile();
                parsed.Load(binary);
                if (parsed.Drawable is null)
                    throw new InvalidDataException($"CodeWalker could not read back the generated YDR: {assetName}");

                var outPath = Path.Combine(streamDir, assetName + ".ydr");
                File.WriteAllBytes(outPath, binary);
                ydrResults.Add(Record(outPath, "YDR", binary));
                Console.WriteLine($"Converted YDR {assetName}: {binary.Length:N0} bytes");
            }

            // CodeWalker stores YMAP / YTYP as RSC Meta resources. Parse their schema-aware
            // XML through XmlMeta's RSC path, then read the generated resource back with the
            // corresponding CodeWalker file class before accepting the result.
            var ytypDocument = LoadXml(ytypXml);
            RequireRoot(ytypDocument, "CMapTypes", ytypXml);
            var ytypBinary = XmlMeta.GetData(ytypDocument, MetaFormat.RSC, string.Empty);
            if (ytypBinary is null || ytypBinary.Length == 0)
                throw new InvalidDataException("CodeWalker did not convert CMapTypes XML to a YTYP resource");
            ValidateRscHeader(ytypBinary, ytypXml);
            var ytypCheck = new YtypFile();
            ytypCheck.Load(ytypBinary);
            var archetypeCount = ytypCheck.AllArchetypes?.Length ?? 0;
            if (archetypeCount < 7)
                throw new InvalidDataException($"Native YTYP readback found {archetypeCount} archetypes; expected at least 7");
            var ytypOut = Path.Combine(streamDir, "dushanbe_istiklol.ytyp");
            File.WriteAllBytes(ytypOut, ytypBinary);
            var ytypRecord = Record(ytypOut, "YTYP", ytypBinary);
            Console.WriteLine($"Converted YTYP: {archetypeCount} archetypes, {ytypBinary.Length:N0} bytes");

            var ymapDocument = LoadXml(ymapXml);
            RequireRoot(ymapDocument, "CMapData", ymapXml);
            var ymapBinary = XmlMeta.GetData(ymapDocument, MetaFormat.RSC, string.Empty);
            if (ymapBinary is null || ymapBinary.Length == 0)
                throw new InvalidDataException("CodeWalker did not convert CMapData XML to a YMAP resource");
            ValidateRscHeader(ymapBinary, ymapXml);
            var ymapCheck = new YmapFile();
            ymapCheck.Load(ymapBinary);
            var entityCount = ymapCheck.AllEntities?.Length ?? 0;
            if (entityCount < 7)
                throw new InvalidDataException($"Native YMAP readback found {entityCount} entities; expected at least 7");
            var ymapOut = Path.Combine(streamDir, "dushanbe_istiklol.ymap");
            File.WriteAllBytes(ymapOut, ymapBinary);
            var ymapRecord = Record(ymapOut, "YMAP", ymapBinary);
            Console.WriteLine($"Converted YMAP: {entityCount} entities, {ymapBinary.Length:N0} bytes");

            var records = ydrResults.Concat(new[] { ytypRecord, ymapRecord }).ToArray();
            var manifest = new
            {
                schema_version = 1,
                project = "GTA-Dushanbe",
                status = "codewalker_gen8_binary_conversion_passed",
                game_ready = false,
                generated_utc = DateTimeOffset.UtcNow,
                converter = "CodeWalker.Core",
                codewalker_target_commit = "485d56bec00262ed7fa472261cce7bbc6202b96e",
                target_game_edition = "GTA V Legacy / GEN8",
                input_format = "Sollumz CodeWalker XML (CWXML)",
                output_resource_format = "RSC7 binary resources",
                coordinate_status = "schematic local coordinates; not GTA V world coordinates",
                ydr_count = ydrResults.Count,
                ytyp_archetype_count = archetypeCount,
                ymap_entity_count = entityCount,
                native_assets = records,
                limitations = new[]
                {
                    "Successful binary conversion and CodeWalker readback are not proof that the map is playable.",
                    "All geometry and positions are schematic; YMAP placements are not tied to verified GTA V world coordinates.",
                    "No collision YBN, proper LOD/SLOD hierarchy, streaming boundary review, or game installation is included.",
                    "The output targets GEN8 / GTA V Legacy only; GEN9 / Enhanced is not tested.",
                    "The Istiklol landmark remains a schematic placeholder until a verified reusable 3D asset or photogrammetry model is acquired.",
            "Original flat-colour placeholder textures and blockout geometry are not final art assets."
                }
            };
            var manifestPath = Path.Combine(outputDir, "native_conversion_manifest.json");
            File.WriteAllText(
                manifestPath,
                JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }),
                new UTF8Encoding(false));

            Console.WriteLine($"CODEWALKER_GEN8_BINARY_CONVERSION_OK: {records.Length} assets");
            Console.WriteLine($"Output: {streamDir}");
            Console.WriteLine($"Manifest: {manifestPath}");
            Console.WriteLine("NOT GAME-READY: in-game validation, world coordinates, collision and LOD work remain.");
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("CODEWALKER_GEN8_BINARY_CONVERSION_FAILED");
            Console.Error.WriteLine(ex);
            return 1;
        }
    }

    private static XmlDocument LoadXml(string path)
    {
        var document = new XmlDocument { XmlResolver = null };
        document.Load(path);
        return document;
    }

    private static void RequireRoot(XmlDocument document, string expected, string path)
    {
        if (!string.Equals(document.DocumentElement?.Name, expected, StringComparison.Ordinal))
            throw new InvalidDataException(
                $"Unexpected XML root in {Path.GetFileName(path)}: {document.DocumentElement?.Name ?? "(none)"}; expected {expected}");
    }

    private static void ValidateRscHeader(byte[] data, string source)
    {
        if (data.Length < 128)
            throw new InvalidDataException($"Resource generated from {source} is too small: {data.Length} bytes");
        var magic = Encoding.ASCII.GetString(data, 0, 4);
        if (!string.Equals(magic, ExpectedRscMagic, StringComparison.Ordinal))
            throw new InvalidDataException(
                $"Resource generated from {source} has magic '{magic}', not {ExpectedRscMagic}");
    }

    private static NativeAssetRecord Record(string path, string type, byte[] data)
    {
        return new NativeAssetRecord(
            Path.GetRelativePath(Path.GetDirectoryName(Path.GetDirectoryName(path))!, path).Replace('\\', '/'),
            type,
            data.LongLength,
            Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant());
    }

    private sealed record NativeAssetRecord(string path, string type, long size_bytes, string sha256);
}
