using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Linq;

using AssetStudio;
using System.Net;
using System.Collections;

namespace LegendsData
{
    class Program
    {
        //const int LAST_KNOWN_DEFAULT = 7575;
        //const int LAST_KNOWN_DEFAULT = 7581;
        //const int LAST_KNOWN_DEFAULT = 7585;
        //const int LAST_KNOWN_DEFAULT = 7586;
        const int LAST_KNOWN_DEFAULT = 7587;

        public static AssetsManager assetsManager = new AssetsManager();

        static void Main(string[] args)
        {
            int last_known = LAST_KNOWN_DEFAULT;
            if (args.Length == 1)
            {
                if (!int.TryParse(args[0], out last_known))
                {
                    last_known = LAST_KNOWN_DEFAULT;
                }
            }

            bool download = false;

            if (download)
            {
                var assetsBaseUrl = Utils.GetLastAssetUrl(last_known);

                Console.Write(string.Format("Downloading {0}/bindata...", assetsBaseUrl));

                using (var client = new WebClient())
                {
                    client.DownloadFile(string.Format("{0}/bindata", assetsBaseUrl), string.Format("{0}bindata", Path.GetTempPath()));
                }

                Console.WriteLine("done!");

                Console.Write(string.Format("Downloading {0}/localization...", assetsBaseUrl));

                using (var client = new WebClient())
                {
                    client.DownloadFile(string.Format("{0}/localization", assetsBaseUrl), string.Format("{0}localization", Path.GetTempPath()));
                }

                Console.WriteLine("done!");
            }

            string outPath = Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);

            // ensure paths
            Directory.CreateDirectory(Path.Combine(Path.GetTempPath(), "extracted"));
            Directory.CreateDirectory(Path.Combine(outPath, "extracted"));

            // extract with AssetBundle
            if (download)
            {
                assetsManager.LoadFiles(new[] { string.Format("{0}bindata", Path.GetTempPath()), string.Format("{0}localization", Path.GetTempPath()) });
            }
            else
            {
                assetsManager.LoadFiles(new[] {
                "/Applications/Star Trek.app/Contents/Resources/Data/StreamingAssets/AssetBundles/OSX/OSXRed/bindata",
                "/Applications/Star Trek.app/Contents/Resources/Data/StreamingAssets/AssetBundles/OSX/OSXRed/localization",
            });
            }

            foreach (AssetStudio.Object asset in assetsManager.assetsFileList[1].Objects)
            {
                if (asset is AssetStudio.MonoBehaviour)
                {
                    var monoBehaviour = asset as AssetStudio.MonoBehaviour;

                    var type = monoBehaviour.ToType();
                    var str = JsonConvert.SerializeObject(type);
                    File.WriteAllText(Path.Combine(outPath, "extracted", monoBehaviour.m_Name + ".json"), str);
                }
            }

            foreach (AssetStudio.Object asset in assetsManager.assetsFileList[0].Objects)
            {
                if (asset is AssetStudio.TextAsset)
                {
                    var textAsset = asset as AssetStudio.TextAsset;

                    File.WriteAllBytes(Path.Combine(Path.GetTempPath(), "extracted", textAsset.m_Name), textAsset.m_Script);
                }
            }

            DeserializeData deserializeData = new DeserializeData(Path.Combine(Path.GetTempPath(), "extracted"), Path.Combine(outPath, "extracted"));
            deserializeData.Start();
        }
    }

    public class ListDictionaryConverter : JsonConverter
    {
        private static (Type kvp, Type list, Type enumerable, Type[] args) GetTypes(Type objectType)
        {
            var args = objectType.GenericTypeArguments;
            var kvpType = typeof(KeyValuePair<,>).MakeGenericType(args);
            var listType = typeof(List<>).MakeGenericType(kvpType);
            var enumerableType = typeof(IEnumerable<>).MakeGenericType(kvpType);

            return (kvpType, listType, enumerableType, args);
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            /*var (kvpType, listType, _, args) = GetTypes(value.GetType());

            var keys = ((IDictionary)value).Keys.GetEnumerator();
            var values = ((IDictionary)value).Values.GetEnumerator();
            var cl = listType.GetConstructor(Array.Empty<Type>());
            var ckvp = kvpType.GetConstructor(args);

            var list = (IList)cl!.Invoke(Array.Empty<object>());
            while (keys.MoveNext() && values.MoveNext())
            {
                list.Add(ckvp!.Invoke(new[] { keys.Current, values.Current }));
            }

            serializer.Serialize(writer, list);*/

            var dictionary = (IDictionary)value;

            writer.WriteStartArray();

            var en = dictionary.GetEnumerator();
            while (en.MoveNext())
            {
                writer.WriteStartArray();
                serializer.Serialize(writer, en.Key.ToString());
                serializer.Serialize(writer, en.Value);
                writer.WriteEndArray();
            }

            writer.WriteEndArray();
        }

        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
            var (_, listType, enumerableType, args) = GetTypes(objectType);

            var list = ((IList)(serializer.Deserialize(reader, listType)));

            var ci = objectType.GetConstructor(new[] { enumerableType });
            if (ci == null)
            {
                ci = typeof(Dictionary<,>).MakeGenericType(args).GetConstructor(new[] { enumerableType });
            }

            var dict = (IDictionary)ci!.Invoke(new object[] { list });

            return dict;
        }

        public override bool CanConvert(Type objectType)
        {
            if (!objectType.IsGenericType) return objectType.IsAssignableTo(typeof(IDictionary));

            var args = objectType.GenericTypeArguments;
            return args.Length == 2 && objectType.IsAssignableTo(typeof(IDictionary<,>).MakeGenericType(args));
        }
    }

    public class DeserializeData
    {
        private string _basePath;
        private string _outPath;

        public DeserializeData(string basePath, string outPath)
        {
            _basePath = basePath;
            _outPath = outPath;
        }

        private string toJson(object obj)
        {
            JsonSerializerSettings settings = new JsonSerializerSettings();
            settings.Formatting = Formatting.Indented;
            settings.NullValueHandling = NullValueHandling.Ignore;
            settings.MissingMemberHandling = MissingMemberHandling.Ignore;
            settings.Converters = new JsonConverter[] { new StringEnumConverter()/*, new ListDictionaryConverter()*/ };
            settings.Error = (sender, args) =>
            {
                args.ErrorContext.Handled = true;
            };

            return JsonConvert.SerializeObject(obj, settings);
        }

        private void convertBytesToJson(string name, string fixUp = "")
        {
            Console.Write(string.Format("Parsing {0}...", name));
            try
            {
                BinaryFormatter formatter = new BinaryFormatter();
                using (FileStream fs = File.Open(Path.Combine(_basePath, name), FileMode.Open))
                {
                    object obj = formatter.Deserialize(fs);

                    using (FileStream fsJson = File.Create(Path.Combine(_outPath, name + ".json")))
                    {
                        string value = toJson(obj);
                        if (!string.IsNullOrEmpty(fixUp))
                        {
                            int i = 0;
                            value = Regex.Replace(value, fixUp, (match) => string.Format("{0}{1} ", fixUp, i++));
                        }

                        byte[] info = new System.Text.UTF8Encoding(true).GetBytes(value);
                        fsJson.Write(info, 0, info.Length);
                    }
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine("failed!");
                return;
            }

            Console.WriteLine("done!");
        }

        public void Start()
        {
            convertBytesToJson("BattleModifier");
            convertBytesToJson("ContextualTooltip");
            convertBytesToJson("GSAIProfile");
            convertBytesToJson("GSAccessoryItems");
            convertBytesToJson("GSAccessoryStatGeneration");
            convertBytesToJson("GSAccessoryStatGrowth", "GSAccessoryKey1");
            convertBytesToJson("GSAccessoryUpgrading", "GSAccessoryKey");
            convertBytesToJson("GSAccountCreate");
            convertBytesToJson("GSAccountLevel");
            convertBytesToJson("GSAllianceEmblem");
            convertBytesToJson("GSAllianceNameComponent");
            convertBytesToJson("GSAllianceRaid");
            convertBytesToJson("GSAllianceRaidPowerup");
            convertBytesToJson("GSAllianceRaidReward");
            convertBytesToJson("GSBaseStat");
            convertBytesToJson("GSBattle");
            convertBytesToJson("GSBattleEnemy");
            convertBytesToJson("GSBattleModifier");
            convertBytesToJson("GSBotCharacters");
            convertBytesToJson("GSBotEquipment");
            convertBytesToJson("GSBotName");
            convertBytesToJson("GSBotPools");
            convertBytesToJson("GSBotTeamComp");
            convertBytesToJson("GSCharacter");
            convertBytesToJson("GSContextualTooltip");
            convertBytesToJson("GSCrafting");
            convertBytesToJson("GSCutSceneDialogue");
            convertBytesToJson("GSCutSceneStory");
            convertBytesToJson("GSDailyToken");
            convertBytesToJson("GSDefaultBridgeCrew");
            convertBytesToJson("GSDeviceData");
            convertBytesToJson("GSDirectives");
            convertBytesToJson("GSEffect");
            convertBytesToJson("GSEffectType");
            convertBytesToJson("GSEpisodes");
            convertBytesToJson("GSEventTypeFaction");
            convertBytesToJson("GSEventTypeSolo");
            convertBytesToJson("GSEvents");
            convertBytesToJson("GSFactions");
            convertBytesToJson("GSFeatureUnlock");
            convertBytesToJson("GSGear");
            convertBytesToJson("GSGearLevel");
            convertBytesToJson("GSGearUpgrade");
            convertBytesToJson("GSGlossary");
            convertBytesToJson("GSItem");
            convertBytesToJson("GSItemGroups");
            convertBytesToJson("GSLevel");
            convertBytesToJson("GSLoginCalendar");
            convertBytesToJson("GSLoginCalendarGroup");
            convertBytesToJson("GSLoginCalendarGroupDay");
            convertBytesToJson("GSMilestoneRewards");
            convertBytesToJson("GSMissionEffects");
            convertBytesToJson("GSMissionNodes");
            convertBytesToJson("GSMissionObjective");
            convertBytesToJson("GSMissionRewards");
            convertBytesToJson("GSMissions");
            convertBytesToJson("GSMorale");
            convertBytesToJson("GSNews");
            convertBytesToJson("GSNodeEncounter");
            convertBytesToJson("GSNodeExploration");
            convertBytesToJson("GSNodeMapData");
            convertBytesToJson("GSNodeReplayRewards");
            convertBytesToJson("GSNodeRewards");
            convertBytesToJson("GSNotchOverride");
            convertBytesToJson("GSNotifications");
            convertBytesToJson("GSOperation");
            convertBytesToJson("GSOperationBattle");
            convertBytesToJson("GSPlayerNameGenerator");
            convertBytesToJson("GSProperties");
            convertBytesToJson("GSPvPDailyChests");
            convertBytesToJson("GSPvPLeagues");
            convertBytesToJson("GSQuip");
            convertBytesToJson("GSRank");
            convertBytesToJson("GSRarity");
            convertBytesToJson("GSReplayRewards");
            convertBytesToJson("GSSeasonsLeaderboard");
            convertBytesToJson("GSSeasonsPoints");
            convertBytesToJson("GSSeasonsProperties");
            convertBytesToJson("GSSeasonsRewardTiers");
            convertBytesToJson("GSShuttlecraft");
            convertBytesToJson("GSSkill");
            convertBytesToJson("GSSkillUpgrade");
            convertBytesToJson("GSStoreConversionCost");
            convertBytesToJson("GSStoreItem");
            convertBytesToJson("GSSummonItems");
            convertBytesToJson("GSSummonPools");
            convertBytesToJson("GSSummonSetup");
            convertBytesToJson("GSTask");
            convertBytesToJson("GSTaskAchievements");
            convertBytesToJson("GSTaskDaily");
            convertBytesToJson("GSTaskDailySets");
            convertBytesToJson("GSTaskEvent");
            convertBytesToJson("GSTaskEventSets");
            convertBytesToJson("GSTips");
            convertBytesToJson("GSTooltip");
            convertBytesToJson("Item");
            convertBytesToJson("NodeRewards");
        }
    }

    public class Utils
    {
        public static string GetLastAssetUrl(int last_known)
        {
            string assetBundleLocation = getLatestGood(last_known);

            return string.Format("{0}/OSX/OSXRed", assetBundleLocation);
        }

        static async Task<string> getConfig(int buildNumber)
        {
            try
            {
                var url = string.Format("http://cdn0.client-files.proj-red.emeraldcitygames.ca/endpoints/stable1/v{0}/stable1-OSX-release-endpoint.json?ts=timestamp", buildNumber);

                using var client = new HttpClient();

                var content = await client.GetStringAsync(url);

                return JObject.Parse(content).SelectToken("assetBundleLocation").Value<string>();
            }
            catch
            {
                return string.Empty;
            }
        }

        static string getLatestGood(int last_known)
        {
            List<string> urls = new List<string>();

            var tasks = new List<Task>();

            for (int i = last_known; i < last_known + 10; i++)
            {
                tasks.Add(getConfig(i).ContinueWith((url) =>
                {
                    lock (urls)
                    {
                        urls.Add(url.Result);
                    }
                }));
            }

            Task t = Task.WhenAll(tasks);
            try
            {
                t.Wait();
            }
            catch { }

            urls.Sort();

            return urls[urls.Count - 1];
        }
    }
}