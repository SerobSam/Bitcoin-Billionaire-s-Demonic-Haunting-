using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GenesisProtocol
{
    public class GenesisPrototype : MonoBehaviour
    {
        public static GenesisPrototype Instance { get; private set; }
        readonly Dictionary<string, Vector3> fastTravel = new();
        readonly List<GenesisEnemy> enemies = new();
        readonly List<GameObject> missionObjects = new();
        CharacterController controller;
        Camera cam;
        Vector3 velocity;
        float health = 100f;
        int evidence;
        int hashrate = 100;
        string objective = "Reach the Operations Tower";
        string message = "WASTELANDS RESEARCH HUB // INITIALIZING";
        bool missionActive;
        bool bossActive;
        int missionStep;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Boot() => SceneManager.sceneLoaded += (_, __) => EnsureBootstrap();

        static void EnsureBootstrap()
        {
            if (FindObjectOfType<GenesisPrototype>() != null) return;
            var go = new GameObject("GenesisProtocol_Runtime");
            DontDestroyOnLoad(go);
            go.AddComponent<GenesisPrototype>();
        }

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            BuildHub();
            BuildPlayer();
            BuildUI();
        }

        Material Mat(Color color, float metallic = .15f, float emission = 0f)
        {
            var m = new Material(Shader.Find("Standard"));
            m.color = color; m.SetFloat("_Metallic", metallic); m.SetFloat("_Glossiness", .55f);
            if (emission > 0f) { m.EnableKeyword("_EMISSION"); m.SetColor("_EmissionColor", color * emission); }
            return m;
        }

        GameObject Cube(string name, Vector3 pos, Vector3 scale, Material mat, bool collider = true)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = name; go.transform.SetPositionAndRotation(pos, Quaternion.identity); go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = mat;
            if (!collider) Destroy(go.GetComponent<Collider>());
            return go;
        }

        GameObject Pillar(string name, Vector3 pos, float radius, float height, Material mat)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder); go.name = name; go.transform.position = pos; go.transform.localScale = new Vector3(radius, height, radius); go.GetComponent<Renderer>().sharedMaterial = mat; return go;
        }

        void BuildHub()
        {
            var ground = Mat(new Color(.09f,.12f,.14f), .4f); var metal = Mat(new Color(.18f,.22f,.25f), .75f); var glass = Mat(new Color(.08f,.35f,.5f), .1f, 2.2f); var neon = Mat(new Color(.1f,.75f,1f), .05f, 3f); var danger = Mat(new Color(.75f,.06f,.04f), .3f, 2f); var dark = Mat(new Color(.035f,.04f,.05f), .2f);
            Cube("Hub_Ground", new Vector3(0,-1,0), new Vector3(180,2,180), ground);
            // Main plaza and operations tower.
            Cube("Operations_Base", new Vector3(0,2,0), new Vector3(28,6,28), metal);
            Pillar("Genesis_Tower", new Vector3(0,14,0), 7, 14, glass);
            Pillar("Genesis_Signal", new Vector3(0,29,0), 1.2f, 15, neon);
            for (int i=0;i<8;i++) { float a=i*Mathf.PI/4f; var p=new Vector3(Mathf.Cos(a)*22,4,Mathf.Sin(a)*22); Cube("Plaza_Wing",p,new Vector3(10,8,5),metal); }
            // Research ring, hangar, reactor court and underground entrance.
            Cube("Research_Ring", new Vector3(-48,3,22), new Vector3(30,8,24), metal);
            Cube("Hangar", new Vector3(46,4,25), new Vector3(32,10,25), dark);
            Cube("Reactor_Court", new Vector3(48,1,-34), new Vector3(34,4,30), danger);
            Cube("Underground_Gate", new Vector3(-42,3,-38), new Vector3(26,8,18), dark);
            // Rooftop traversal spine.
            for (int i=0;i<6;i++) { float z=48+i*8; Cube("Traversal_Catwalk", new Vector3(0,7+i*2,z), new Vector3(4,1,7), neon); }
            Cube("Cliff_Relay", new Vector3(-62,12,52), new Vector3(12,24,12), metal);
            // Stealth cover and service tunnel props.
            for (int i=0;i<12;i++) { float x=-58+(i%4)*9; float z=-4+(i/4)*9; Cube("Stealth_Cover", new Vector3(x,2,z), new Vector3(5,4,2), dark); }
            // Evidence network: glowing fragments distributed through hub.
            Vector3[] evidencePos = {new(-14,3,10),new(16,3,12),new(-20,8,24),new(23,5,-4),new(-49,8,27),new(45,7,20),new(50,5,-42),new(-46,7,-31),new(7,13,46),new(-61,16,53),new(10,3,-52),new(35,5,-30)};
            for (int i=0;i<evidencePos.Length;i++) { var e=GameObject.CreatePrimitive(PrimitiveType.Sphere); e.name=$"Evidence_{i+1:00}"; e.transform.position=evidencePos[i]; e.transform.localScale=Vector3.one*1.2f; e.GetComponent<Renderer>().sharedMaterial=neon; var pick=e.AddComponent<GenesisInteractable>(); pick.kind=InteractKind.Evidence; pick.label=$"Evidence Fragment {i+1}"; }
            // NPC and mission terminals.
            AddTerminal("MAIN STORY // OPERATIONS", new Vector3(0,5,14), "Main Story", neon);
            AddTerminal("SIDE MISSIONS // FIELD OFFICE", new Vector3(-48,8,10), "Side Mission", neon);
            AddTerminal("UPGRADE STATION // FARADAY FORGE", new Vector3(48,7,25), "Upgrade", glass);
            AddTerminal("MEDICAL BAY", new Vector3(48,7,32), "Heal", glass);
            // Fast travel nodes.
            AddBeacon("Hub Core Beacon", new Vector3(0,4,-18), new Vector3(0,2,0));
            AddBeacon("Research Ring Beacon", new Vector3(-48,8,34), new Vector3(-48,8,34));
            AddBeacon("Cliff Relay", new Vector3(-62,25,52), new Vector3(-62,25,52));
            AddBeacon("Underground Gate", new Vector3(-42,8,-28), new Vector3(-42,8,-28));
            AddBeacon("Genesis Tower Beacon", new Vector3(0,30,0), new Vector3(0,30,0));
            // DLC entrances visibly exist from day one.
            AddDlcGate("NEON TOKYO // DLC", new Vector3(72,6,8), new Color(.9f,.1f,1f));
            AddDlcGate("HELL'S DATACENTER // DLC", new Vector3(72,6,-18), new Color(1f,.12f,.03f));
            AddDlcGate("GENESIS EPILOGUE // DLC", new Vector3(72,6,-44), new Color(.5f,.15f,1f));
            // Boss chamber and control volumes are represented by arena walls.
            Cube("Genesis_Breach_Arena", new Vector3(-72,4,-35), new Vector3(28,8,28), danger);
            Cube("Boss_Core", new Vector3(-72,10,-35), new Vector3(5,10,5), neon);
            SpawnEnemy(new Vector3(34,2,-32), "Training Wraith", 60);
            AddLight(new Vector3(0,35,0), neon, 20, 8);
            AddLight(new Vector3(48,10,-34), danger, 18, 7);
            AddLight(new Vector3(-42,10,-38), glass, 15, 6);
        }

        void AddLight(Vector3 pos, Material mat, float range, float intensity)
        { var go=new GameObject("Hub_Light"); go.transform.position=pos; var l=go.AddComponent<Light>(); l.type=LightType.Point; l.color=mat.color; l.range=range; l.intensity=intensity; }

        void AddTerminal(string label, Vector3 pos, string kind, Material mat)
        { Cube(label,pos,new Vector3(4,3,1.5f),mat); var i=GameObject.CreatePrimitive(PrimitiveType.Cube); i.name=label+"_Interact"; i.transform.position=pos+Vector3.forward*1.5f; i.transform.localScale=new Vector3(3,2,.5f); i.GetComponent<Renderer>().sharedMaterial=mat; var x=i.AddComponent<GenesisInteractable>(); x.kind=kind=="Main Story"?InteractKind.MainMission:kind=="Side Mission"?InteractKind.SideMission:kind=="Upgrade"?InteractKind.Upgrade:InteractKind.Heal; x.label=label; }

        void AddBeacon(string label, Vector3 visual, Vector3 destination)
        { Pillar(label,visual,1.4f,3,Mat(new Color(.1f,.7f,1f),.2f,3)); fastTravel[label]=destination; var b=GameObject.CreatePrimitive(PrimitiveType.Sphere); b.name=label+"_Use"; b.transform.position=visual+Vector3.up*3; b.transform.localScale=Vector3.one*1.5f; b.GetComponent<Renderer>().sharedMaterial=Mat(new Color(.1f,.7f,1f),.1f,4); var x=b.AddComponent<GenesisInteractable>(); x.kind=InteractKind.FastTravel; x.label=label; }

        void AddDlcGate(string label, Vector3 pos, Color color)
        { var m=Mat(color,.25f,3); Cube(label,pos,new Vector3(7,12,2),m); Pillar(label+"_R",pos+new Vector3(-5,0,0),1,6,m); Pillar(label+"_L",pos+new Vector3(5,0,0),1,6,m); var x=GameObject.CreatePrimitive(PrimitiveType.Sphere); x.name=label+"_Interact"; x.transform.position=pos+Vector3.up*5; x.transform.localScale=Vector3.one*2; x.GetComponent<Renderer>().sharedMaterial=m; var i=x.AddComponent<GenesisInteractable>(); i.kind=InteractKind.Dlc; i.label=label; }

        void SpawnEnemy(Vector3 pos, string label, float hp)
        { var e=GameObject.CreatePrimitive(PrimitiveType.Capsule); e.name=label; e.transform.position=pos; e.transform.localScale=Vector3.one*2; e.GetComponent<Renderer>().sharedMaterial=Mat(new Color(.65f,.03f,.15f),.1f,2); var ai=e.AddComponent<GenesisEnemy>(); ai.health=hp; ai.label=label; enemies.Add(ai); }

        void BuildPlayer()
        { var go=GameObject.CreatePrimitive(PrimitiveType.Capsule); go.name="Player_Cypherpunk"; go.transform.position=new Vector3(0,2,-8); controller=go.AddComponent<CharacterController>(); controller.height=2; controller.radius=.45f; Destroy(go.GetComponent<Collider>()); var body=go.AddComponent<GenesisPlayer>(); body.owner=this; cam=new GameObject("Player_Camera").AddComponent<Camera>(); cam.transform.SetParent(go.transform); cam.transform.localPosition=new Vector3(0,4,-8); cam.transform.localRotation=Quaternion.Euler(18,0,0); cam.tag="MainCamera"; var light=go.AddComponent<Light>(); light.type=LightType.Point; light.range=7; light.intensity=1; }

        void BuildUI() { }

        public void Move(Vector2 input)
        { Vector3 dir=(transformForward()*input.y + transformRight()*input.x); if(dir.sqrMagnitude>1)dir.Normalize(); controller.Move(dir*7f*Time.deltaTime); if(controller.isGrounded)velocity.y=-1; else velocity.y+=Physics.gravity.y*Time.deltaTime; controller.Move(velocity*Time.deltaTime); }
        Vector3 transformForward()=>new Vector3(cam.transform.forward.x,0,cam.transform.forward.z).normalized;
        Vector3 transformRight()=>new Vector3(cam.transform.right.x,0,cam.transform.right.z).normalized;
        public void Look(float yaw) { cam.transform.RotateAround(controller.transform.position,Vector3.up,yaw); }
        public void Attack() { Ray r=new Ray(cam.transform.position,cam.transform.forward); if(Physics.Raycast(r,out var hit,30)){ var enemy=hit.collider.GetComponent<GenesisEnemy>(); if(enemy!=null)enemy.Damage(28); } }
        public void Interact(GenesisInteractable x)
        { if(x.kind==InteractKind.Evidence){evidence++; Destroy(x.gameObject); message=$"Evidence secured. Total: {evidence}/12"; return;} if(x.kind==InteractKind.MainMission){missionActive=true; missionStep=0; objective="Investigate the Research Ring"; message="MAIN STORY: BEL AIR BLACKOUT // TRACE THE GENESIS SIGNAL"; return;} if(x.kind==InteractKind.SideMission){SpawnEnemy(new Vector3(-30,2,8),"Bounty Wraith",45); message="SIDE MISSION: BOUNTY SIGNAL // DEFEAT THE WRAITH"; objective="Defeat the bounty wraith"; return;} if(x.kind==InteractKind.Upgrade){hashrate+=25; message="Faraday Forge: Hashrate +25"; return;} if(x.kind==InteractKind.Heal){health=100; message="Medical Bay: systems restored"; return;} if(x.kind==InteractKind.FastTravel){controller.enabled=false; controller.transform.position=fastTravel[x.label]+Vector3.up*2; controller.enabled=true; message=$"Fast travel: {x.label}"; return;} if(x.kind==InteractKind.Dlc){message=$"{x.label} is installed in the Hub and awaits DLC ownership/progression."; return;} }
        public void EnemyDefeated(GenesisEnemy e) { enemies.Remove(e); if(missionActive && missionStep==0){missionStep=1; objective="Return to Operations and decode the signal"; message="GENESIS SIGNAL LOCATED // RETURN TO THE TOWER";} else if(missionActive && missionStep==1){missionStep=2; objective="Choose: CLEANSE / EXPLOIT / QUARANTINE"; message="The corrupted fragment is ready for a decision.";} }
        public void Choose(string choice){ if(missionStep<2){message="No decision is ready.";return;} missionActive=false; missionStep=0; objective="Explore the Hub or begin the next mission"; hashrate+=50; message=$"Choice recorded: {choice}. +50 Hashrate. Campaign state advanced."; }
        public void Damage(float amount){health-=amount;if(health<=0){health=100;controller.enabled=false;controller.transform.position=new Vector3(0,2,-8);controller.enabled=true;message="SYSTEM FAILURE // Recovered at Hub Core Beacon";}}
        public void Boss(){if(bossActive)return;bossActive=true;objective="Defeat the Genesis Echo";SpawnEnemy(new Vector3(-72,3,-35),"Genesis Echo",180);message="BOSS ARENA ACTIVE // GENESIS ECHO ONLINE";}
        void OnGUI(){ GUI.Box(new Rect(12,12,460,125),"GENESIS PROTOCOL // WASTELANDS HUB"); GUI.Label(new Rect(28,40,430,24),$"HP {health:0}/100   HASHRATE {hashrate}   EVIDENCE {evidence}/12"); GUI.Label(new Rect(28,66,430,38),$"OBJECTIVE: {objective}"); GUI.Label(new Rect(28,102,430,24),message); GUI.Box(new Rect(Screen.width-285,12,270,112),"CONTROLS"); GUI.Label(new Rect(Screen.width-270,40,245,80),"WASD  Move\nE  Interact / terminals\nLMB  Packet Burn\nR  Cleanse   F  Exploit   Q  Quarantine"); }
        public GenesisInteractable Nearby(){GenesisInteractable best=null;float d=3.5f;foreach(var x in FindObjectsOfType<GenesisInteractable>()){float n=Vector3.Distance(controller.transform.position,x.transform.position);if(n<d){d=n;best=x;}}return best;}
    }

    public enum InteractKind { MainMission, SideMission, Evidence, Upgrade, Heal, FastTravel, Dlc }
    public class GenesisInteractable : MonoBehaviour { public InteractKind kind; public string label; }
    public class GenesisEnemy : MonoBehaviour
    { public float health=50; public string label; float hitTimer; public void Damage(float amount){health-=amount; if(health<=0){GenesisPrototype.Instance.EnemyDefeated(this);Destroy(gameObject);}} void Update(){var p=GenesisPrototype.Instance; if(p==null)return; var target=p.transform; var d=Vector3.Distance(transform.position,target.position); if(d<18){transform.position=Vector3.MoveTowards(transform.position,target.position,2.2f*Time.deltaTime); if(d<2.2f&&Time.time>hitTimer){p.Damage(8);hitTimer=Time.time+1.1f;}}}}
    public class GenesisPlayer : MonoBehaviour
    { public GenesisPrototype owner; void Update(){if(owner==null)return; var move=new Vector2(Input.GetAxisRaw("Horizontal"),Input.GetAxisRaw("Vertical"));owner.Move(move);if(Input.GetMouseButtonDown(0))owner.Attack();if(Input.GetKeyDown(KeyCode.E)){var n=owner.Nearby();if(n)owner.Interact(n);}if(Input.GetKeyDown(KeyCode.R))owner.Choose("CLEANSE");if(Input.GetKeyDown(KeyCode.F))owner.Choose("EXPLOIT");if(Input.GetKeyDown(KeyCode.Q))owner.Choose("QUARANTINE");}}
}
