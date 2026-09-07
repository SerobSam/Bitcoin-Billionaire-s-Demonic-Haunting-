#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor.SceneManagement;

namespace GenesisProtocol.EditorTools
{
    public static class GenesisWorldBuilder
    {
        const string RootName = "GENESIS_PROTOCOL_WORLD";

        [MenuItem("Genesis Protocol/Build Full World Blockout")]
        public static void BuildFullWorld()
        {
            var root = GameObject.Find(RootName);
            if (root != null) Object.DestroyImmediate(root);
            root = new GameObject(RootName);

            CreateRegion(root.transform, "01_Wastelands_Hub", new Vector3(0, 0, 0), 140, 0.10f, "Operations Tower / Research Ring / Genesis Breach");
            CreateRegion(root.transform, "02_Bel_Air_Blackout", new Vector3(240, 0, 0), 120, 0.12f, "Mansion / server vault / blackout streets");
            CreateRegion(root.transform, "03_Irvine_Consensus", new Vector3(0, 0, 240), 120, 0.14f, "Suburbs / cold storage / relay compound");
            CreateRegion(root.transform, "04_Dark_Pool_Dungeons", new Vector3(-240, -12, 0), 110, 0.16f, "Flooded tunnels / Blackwater Choir / Warden arena");
            CreateRegion(root.transform, "05_Zero_State_Relay", new Vector3(0, 20, -240), 130, 0.18f, "Relay towers / sky bridges / final signal");
            CreateRegion(root.transform, "06_Neon_Tokyo_DLC", new Vector3(240, 0, 240), 150, 0.11f, "Shibuya streets / rooftops / Chrome Oni shrine");
            CreateRegion(root.transform, "07_Hells_Datacenter_DLC", new Vector3(-240, 0, -240), 150, 0.20f, "Volcanic servers / cathedral core / infernal firewall");
            CreateRoads(root.transform);
            CreateWorldAnchor(root.transform);
            EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
            Selection.activeGameObject = root;
            Debug.Log("Genesis Protocol full world blockout built. Replace generated primitives with production art as assets become available.");
        }

        static void CreateRegion(Transform parent, string name, Vector3 center, float size, float corruption, string landmarks)
        {
            var region = new GameObject(name);
            region.transform.SetParent(parent);
            region.transform.position = center;
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "Terrain_Blockout";
            floor.transform.SetParent(region.transform);
            floor.transform.localPosition = new Vector3(0, -2, 0);
            floor.transform.localScale = new Vector3(size, 4, size);
            floor.GetComponent<Renderer>().sharedMaterial = MaterialFor(corruption);

            for (int i = 0; i < 8; i++)
            {
                float angle = i * Mathf.PI * 2f / 8f;
                var landmark = GameObject.CreatePrimitive(i % 3 == 0 ? PrimitiveType.Cylinder : PrimitiveType.Cube);
                landmark.name = "Landmark_" + (i + 1).ToString("00");
                landmark.transform.SetParent(region.transform);
                float radius = size * 0.28f;
                landmark.transform.localPosition = new Vector3(Mathf.Cos(angle) * radius, 4 + (i % 3) * 4, Mathf.Sin(angle) * radius);
                landmark.transform.localScale = i % 3 == 0 ? new Vector3(8, 10 + i, 8) : new Vector3(16, 8 + i, 12);
                landmark.GetComponent<Renderer>().sharedMaterial = MaterialFor(corruption + 0.04f);
            }

            var marker = new GameObject("RegionMetadata");
            marker.transform.SetParent(region.transform);
            marker.AddComponent<GenesisRegionMarker>().Initialize(name, landmarks, corruption);
        }

        static void CreateRoads(Transform parent)
        {
            var roads = new GameObject("WORLD_CONNECTIONS");
            roads.transform.SetParent(parent);
            Vector3[] points = { new(0, 0, 0), new(240, 0, 0), new(0, 0, 240), new(-240, -12, 0), new(0, 20, -240), new(240, 0, 240), new(-240, 0, -240) };
            for (int i = 1; i < points.Length; i++)
            {
                var road = GameObject.CreatePrimitive(PrimitiveType.Cube);
                road.name = "WorldRoute_" + i.ToString("00");
                road.transform.SetParent(roads.transform);
                Vector3 a = points[0], b = points[i], delta = b - a;
                road.transform.position = (a + b) * 0.5f;
                road.transform.localScale = new Vector3(Mathf.Max(8, delta.magnitude), 1.5f, 10);
                road.transform.rotation = Quaternion.LookRotation(delta.normalized, Vector3.up) * Quaternion.Euler(0, 90, 0);
            }
        }

        static void CreateWorldAnchor(Transform parent)
        {
            var anchor = new GameObject("WorldMap_StreamingAnchor");
            anchor.transform.SetParent(parent);
            anchor.transform.position = Vector3.zero;
            anchor.AddComponent<GenesisWorldAnchor>();
        }

        static Material MaterialFor(float corruption)
        {
            var material = new Material(Shader.Find("Standard"));
            float c = Mathf.Clamp01(corruption);
            material.color = Color.Lerp(new Color(.12f, .16f, .19f), new Color(.35f, .035f, .12f), c);
            material.SetFloat("_Metallic", Mathf.Lerp(.25f, .75f, c));
            material.SetFloat("_Glossiness", .55f);
            return material;
        }
    }

    public sealed class GenesisRegionMarker : MonoBehaviour
    {
        public string regionId;
        public string landmarks;
        public float corruption;
        public void Initialize(string id, string landmarkList, float corruptionLevel)
        {
            regionId = id;
            landmarks = landmarkList;
            corruption = corruptionLevel;
        }
    }

    public sealed class GenesisWorldAnchor : MonoBehaviour
    {
        public string streamingStrategy = "Addressables region streaming with additive scene loading";
        public string lightingStrategy = "HDRP volume per region";
        public string navigationStrategy = "AI Navigation surface per streamed region";
    }
}
#endif
