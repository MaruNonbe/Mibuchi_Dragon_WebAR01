const HOME_STORAGE_KEY = "nagaiQuartetHomeTarget";
const DEFAULT_RADIUS_METERS = 100;

const STATION_MODEL = {
  modelId: "stationModel",
  fallbackId: "fallbackStationModel",
};

const STATION_VARIANTS = [
  { variantLabel: "きつね・ウサギ・シカの弦楽四重奏", ensemble: "strings", modelPath: "./assets/stations/akayu_strings_fox_rabbit.glb" },
  { variantLabel: "ネコと小鳥の木管アンサンブル", ensemble: "woodwinds", modelPath: "./assets/stations/nanyo_city_hall_cats_woodwinds.glb" },
  { variantLabel: "イヌたちの金管ファンファーレ", ensemble: "brass", modelPath: "./assets/stations/miyauchi_dogs_brass.glb" },
  { variantLabel: "リスとカエルの打楽器パレード", ensemble: "percussion", modelPath: "./assets/stations/orihata_squirrels_percussion.glb" },
  { variantLabel: "パンダとペンギンの駅前ジャズ", ensemble: "jazz", modelPath: "./assets/stations/ringo_panda_penguin_jazz.glb" },
  { variantLabel: "タヌキたちの太鼓リズム", ensemble: "taiko", modelPath: "./assets/stations/nishi_otsuka_tanuki_taiko.glb" },
  { variantLabel: "シカと小鳥のフルート合奏", ensemble: "flute", modelPath: "./assets/stations/imaizumi_deer_flutes.glb" },
  { variantLabel: "クマたちの低音ブラス", ensemble: "low-brass", modelPath: "./assets/stations/tokiniwa_bears_low_brass.glb" },
  { variantLabel: "ウサギたちのクラリネット隊", ensemble: "clarinet", modelPath: "./assets/stations/minami_nagai_rabbit_clarinets.glb" },
  { variantLabel: "どうぶつ弦楽四重奏", ensemble: "strings", modelPath: "./assets/stations/nagai_main_string_quartet.glb" },
  { variantLabel: "小鳥たちのピッコロ行進曲", ensemble: "piccolo", modelPath: "./assets/stations/ayame_koen_birds_piccolo.glb" },
  { variantLabel: "キツネたちのサックスバンド", ensemble: "sax", modelPath: "./assets/stations/uzen_narita_fox_sax_band.glb" },
  { variantLabel: "白ウサギのハンドベル隊", ensemble: "handbell", modelPath: "./assets/stations/shirousagi_white_rabbit_bells.glb" },
  { variantLabel: "カモシカたちのホルン合奏", ensemble: "horn", modelPath: "./assets/stations/koguwa_kamoshika_horns.glb" },
  { variantLabel: "カエルたちのマリンバ隊", ensemble: "marimba", modelPath: "./assets/stations/ayukai_frogs_marimba.glb" },
  { variantLabel: "ヒツジたちのトロンボーン隊", ensemble: "trombone", modelPath: "./assets/stations/shikinosato_sheep_trombones.glb" },
  { variantLabel: "全員集合フィナーレ", ensemble: "finale", modelPath: "./assets/stations/arato_finale_all_stars.glb" },
];

const FLOWER_NAGAI_STATIONS = [
  { name: "赤湯駅", latitude: 38.0477732, longitude: 140.1489173 },
  { name: "南陽市役所駅", latitude: 38.0553737, longitude: 140.1491345 },
  { name: "宮内駅", latitude: 38.0709227, longitude: 140.1350999 },
  { name: "おりはた駅", latitude: 38.0664757, longitude: 140.1225351 },
  { name: "梨郷駅", latitude: 38.0573441, longitude: 140.0985199 },
  { name: "西大塚駅", latitude: 38.0553858, longitude: 140.0643104 },
  { name: "今泉駅", latitude: 38.0570157, longitude: 140.0442391 },
  { name: "時庭駅", latitude: 38.0768771, longitude: 140.0297508 },
  { name: "南長井駅", latitude: 38.0974434, longitude: 140.0346592 },
  { name: "長井駅", latitude: 38.1065942, longitude: 140.0336548 },
  { name: "あやめ公園駅", latitude: 38.1140176, longitude: 140.0326945 },
  { name: "羽前成田駅", latitude: 38.1309784, longitude: 140.0351477 },
  { name: "白兎駅", latitude: 38.1501321, longitude: 140.0410764 },
  { name: "蚕桑駅", latitude: 38.1613789, longitude: 140.0468579 },
  { name: "鮎貝駅", latitude: 38.1826087, longitude: 140.0710219 },
  { name: "四季の郷駅", latitude: 38.1858218, longitude: 140.0776309 },
  { name: "荒砥駅", latitude: 38.1879827, longitude: 140.0975825 },
];

const TARGETS = [
  ...FLOWER_NAGAI_STATIONS.map((station, index) => ({
    ...station,
    ...STATION_VARIANTS[index % STATION_VARIANTS.length],
    ...STATION_MODEL,
    radiusMeters: DEFAULT_RADIUS_METERS,
  })),
  {
    name: "タスパークホテル長井 検証地点",
    latitude: 38.1013040,
    longitude: 140.0433785,
    radiusMeters: DEFAULT_RADIUS_METERS,
    ...STATION_MODEL,
    modelPath: "./assets/stations/nagai_main_string_quartet.glb",
    variantLabel: "検証用どうぶつアンサンブル",
    ensemble: "test",
  },
];

const gate = document.getElementById("gate");
const startButton = document.getElementById("startButton");
const saveHomeButton = document.getElementById("saveHomeButton");
const statusTitle = document.getElementById("statusTitle");
const distanceText = document.getElementById("distanceText");
const outside = document.getElementById("outside");
const outsideDistance = document.getElementById("outsideDistance");
const cameraFeed = document.getElementById("cameraFeed");
const previewPanel = document.getElementById("previewPanel");
const previewStationSelect = document.getElementById("previewStationSelect");
const previewPrev = document.getElementById("previewPrev");
const previewNext = document.getElementById("previewNext");
const gpsModeButton = document.getElementById("gpsModeButton");
const musicButton = document.getElementById("musicButton");
const photoGuidePanel = document.getElementById("photoGuidePanel");
const modelSmallerButton = document.getElementById("modelSmallerButton");
const modelLargerButton = document.getElementById("modelLargerButton");
const childGuideButton = document.getElementById("childGuideButton");
const childGuideOverlay = document.getElementById("childGuideOverlay");
const stationModel = document.getElementById(STATION_MODEL.modelId);
const fallbackStationModel = document.getElementById(STATION_MODEL.fallbackId);
const arEntities = [stationModel, fallbackStationModel].filter(Boolean);
const stationTargets = TARGETS.slice(0, FLOWER_NAGAI_STATIONS.length);

let announcedTargetName = "";
let started = false;
let activeTarget = null;
let previewTarget = null;
let visibleStateKey = "";
let hasLatchedVisibleTarget = false;
let lastStatusUpdateMs = 0;
let latestPosition = null;

let runtimeAnimation = null;
const modelLoadState = {};
let activeModelPath = "";
let audioContext = null;
let musicTimer = null;
let musicPlaying = false;
let nextMusicTime = 0;
let musicStep = 0;
let musicNoiseBuffer = null;
let modelScaleIndex = 1;
let childGuideVisible = true;

const MUSIC_BPM = 112;
const MUSIC_STEP_SECONDS = 60 / MUSIC_BPM / 2;
const MUSIC_LOOKAHEAD_SECONDS = 0.45;
const MUSIC_SCHEDULE_MS = 90;
const MUSIC_SCALE_MIDI = [60, 62, 64, 67, 69, 72, 74, 76];
const MUSIC_MELODY = [0, 2, 4, 5, 4, 2, 1, 2, 0, 2, 4, 7, 6, 4, 2, 1];
const MUSIC_CHORD_ROOTS = [60, 67, 69, 65, 60, 67, 65, 67];
const MODEL_SCALE_OPTIONS = [0.65, 0.80, 0.95, 1.10];

function loadSavedHomeTarget() {
  try {
    const raw = window.localStorage.getItem(HOME_STORAGE_KEY);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    if (typeof parsed.latitude !== "number" || typeof parsed.longitude !== "number") {
      return null;
    }

    return {
      name: "自宅テスト地点",
      latitude: parsed.latitude,
      longitude: parsed.longitude,
      radiusMeters: parsed.radiusMeters || DEFAULT_RADIUS_METERS,
      ...STATION_MODEL,
      modelPath: "./assets/stations/nagai_main_string_quartet.glb",
      variantLabel: "自宅検証用どうぶつアンサンブル",
      ensemble: "home-test",
    };
  } catch {
    return null;
  }
}

function addSavedHomeTarget() {
  const savedHome = loadSavedHomeTarget();
  if (!savedHome) {
    return;
  }

  const exists = TARGETS.some((target) => target.name === savedHome.name);
  if (!exists) {
    TARGETS.push(savedHome);
  }
}

addSavedHomeTarget();

function midiToFrequency(note) {
  return 440 * Math.pow(2, (note - 69) / 12);
}

function ensureAudioContext() {
  if (!audioContext) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioContext = new AudioContextClass();
  }
  if (!musicNoiseBuffer) {
    const length = audioContext.sampleRate * 0.28;
    musicNoiseBuffer = audioContext.createBuffer(1, length, audioContext.sampleRate);
    const data = musicNoiseBuffer.getChannelData(0);
    for (let i = 0; i < length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 2.4);
    }
  }
  return audioContext;
}

function ensembleSound(target) {
  const ensemble = target?.ensemble || "strings";
  if (["woodwinds", "flute", "clarinet", "piccolo"].includes(ensemble)) {
    return { melody: "triangle", harmony: "sine", bass: "triangle", percussion: false, brightness: 0.34 };
  }
  if (["brass", "low-brass", "horn", "trombone", "sax"].includes(ensemble)) {
    return { melody: "sawtooth", harmony: "triangle", bass: "sawtooth", percussion: false, brightness: 0.25 };
  }
  if (["percussion", "taiko", "handbell", "marimba"].includes(ensemble)) {
    return { melody: "sine", harmony: "triangle", bass: "sine", percussion: true, brightness: 0.42 };
  }
  if (ensemble === "finale" || ensemble === "jazz") {
    return { melody: "triangle", harmony: "sawtooth", bass: "triangle", percussion: true, brightness: 0.32 };
  }
  return { melody: "triangle", harmony: "sine", bass: "triangle", percussion: false, brightness: 0.30 };
}

function playTone(time, frequency, duration, type, gainValue) {
  const ctx = ensureAudioContext();
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, time);
  filter.type = "lowpass";
  filter.frequency.setValueAtTime(1800 + frequency * 1.8, time);
  gain.gain.setValueAtTime(0.0001, time);
  gain.gain.exponentialRampToValueAtTime(Math.max(gainValue, 0.0001), time + 0.025);
  gain.gain.exponentialRampToValueAtTime(0.0001, time + duration);

  oscillator.connect(filter);
  filter.connect(gain);
  gain.connect(ctx.destination);
  oscillator.start(time);
  oscillator.stop(time + duration + 0.05);
}

function playNoise(time, gainValue) {
  const ctx = ensureAudioContext();
  const source = ctx.createBufferSource();
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  source.buffer = musicNoiseBuffer;
  filter.type = "bandpass";
  filter.frequency.setValueAtTime(900, time);
  filter.Q.setValueAtTime(0.8, time);
  gain.gain.setValueAtTime(gainValue, time);
  gain.gain.exponentialRampToValueAtTime(0.0001, time + 0.12);

  source.connect(filter);
  filter.connect(gain);
  gain.connect(ctx.destination);
  source.start(time);
}

function scheduleMusicStep(step, time) {
  const sound = ensembleSound(activeTarget);
  const melodyNote = MUSIC_SCALE_MIDI[MUSIC_MELODY[step % MUSIC_MELODY.length] % MUSIC_SCALE_MIDI.length];
  const chordRoot = MUSIC_CHORD_ROOTS[Math.floor(step / 2) % MUSIC_CHORD_ROOTS.length];
  const accent = step % 8 === 0 ? 1.15 : 1.0;

  playTone(time, midiToFrequency(melodyNote + 12), MUSIC_STEP_SECONDS * 1.7, sound.melody, 0.045 * accent);

  if (step % 2 === 0) {
    playTone(time, midiToFrequency(chordRoot), MUSIC_STEP_SECONDS * 1.9, sound.bass, 0.026);
  }

  if (step % 4 === 0) {
    playTone(time + 0.01, midiToFrequency(chordRoot + 7), MUSIC_STEP_SECONDS * 2.6, sound.harmony, 0.018 * sound.brightness);
    playTone(time + 0.02, midiToFrequency(chordRoot + 12), MUSIC_STEP_SECONDS * 2.6, sound.harmony, 0.014 * sound.brightness);
  }

  if (sound.percussion) {
    if (step % 4 === 0) {
      playTone(time, midiToFrequency(48), 0.09, "sine", 0.055);
    }
    if (step % 4 === 2) {
      playNoise(time, 0.022);
    }
  }
}

function musicScheduler() {
  const ctx = ensureAudioContext();
  while (nextMusicTime < ctx.currentTime + MUSIC_LOOKAHEAD_SECONDS) {
    scheduleMusicStep(musicStep, nextMusicTime);
    nextMusicTime += MUSIC_STEP_SECONDS;
    musicStep += 1;
  }
}

function updateMusicButton() {
  if (!musicButton) {
    return;
  }
  musicButton.textContent = musicPlaying ? "音楽ON" : "音楽";
  musicButton.classList.toggle("is-playing", musicPlaying);
}

function currentModelScale() {
  return MODEL_SCALE_OPTIONS[modelScaleIndex] || 0.80;
}

function applyModelScale() {
  const scale = currentModelScale();
  if (stationModel?.object3D) {
    stationModel.object3D.scale.set(scale, scale, scale);
  }
}

function updatePhotoGuideControls() {
  if (modelSmallerButton) {
    modelSmallerButton.disabled = modelScaleIndex <= 0;
  }
  if (modelLargerButton) {
    modelLargerButton.disabled = modelScaleIndex >= MODEL_SCALE_OPTIONS.length - 1;
  }
  childGuideButton?.classList.toggle("is-active", childGuideVisible);
  childGuideOverlay?.classList.toggle("hidden", !childGuideVisible || !activeTarget);
}

function adjustModelScale(delta) {
  const nextIndex = Math.min(Math.max(modelScaleIndex + delta, 0), MODEL_SCALE_OPTIONS.length - 1);
  if (nextIndex === modelScaleIndex) {
    return;
  }
  modelScaleIndex = nextIndex;
  applyModelScale();
  updatePhotoGuideControls();
}

function toggleChildGuide() {
  childGuideVisible = !childGuideVisible;
  updatePhotoGuideControls();
}

async function toggleMusic() {
  const ctx = ensureAudioContext();
  if (ctx.state === "suspended") {
    await ctx.resume();
  }

  if (musicPlaying) {
    window.clearInterval(musicTimer);
    musicTimer = null;
    musicPlaying = false;
    updateMusicButton();
    return;
  }

  nextMusicTime = ctx.currentTime + 0.08;
  musicStep = 0;
  musicScheduler();
  musicTimer = window.setInterval(musicScheduler, MUSIC_SCHEDULE_MS);
  musicPlaying = true;
  updateMusicButton();
}

function setupPreviewControls() {
  stationTargets.forEach((target, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${target.name} / ${target.variantLabel}`;
    previewStationSelect.appendChild(option);
  });
}

function activatePreviewTarget(index) {
  const normalizedIndex = (index + stationTargets.length) % stationTargets.length;
  previewStationSelect.value = String(normalizedIndex);
  previewTarget = stationTargets[normalizedIndex];
  activeTarget = previewTarget;
  hasLatchedVisibleTarget = true;
  visibleStateKey = "";
  setVisible(activeTarget);
  outside.classList.add("hidden");
  announcedTargetName = "";
  updatePreviewStatus();
}

function updatePreviewStatus() {
  if (!previewTarget) {
    return;
  }

  let distancePart = "現在地で評価表示中";
  if (latestPosition) {
    const distance = distanceMeters(
      latestPosition.coords.latitude,
      latestPosition.coords.longitude,
      previewTarget.latitude,
      previewTarget.longitude,
    );
    const accuracy = Math.round(latestPosition.coords.accuracy || 0);
    distancePart = `本来の駅まで約${Math.round(distance)}m / GPS精度 約${accuracy}m`;
  }

  statusTitle.textContent = `評価モード / 駅別キャラ v26`;
  distanceText.textContent = `${previewTarget.name} / ${previewTarget.variantLabel} / ${distancePart}`;
}

function clearPreviewTarget() {
  previewTarget = null;
  activeTarget = null;
  hasLatchedVisibleTarget = false;
  announcedTargetName = "";
  visibleStateKey = "";
  setVisible(null);
  statusTitle.textContent = "GPSモード";
  distanceText.textContent = "現在地が表示エリアに入るとARが表示されます";
}

function distanceMeters(aLat, aLon, bLat, bLon) {
  const earthRadius = 6371000;
  const toRad = (value) => (value * Math.PI) / 180;
  const dLat = toRad(bLat - aLat);
  const dLon = toRad(bLon - aLon);
  const lat1 = toRad(aLat);
  const lat2 = toRad(bLat);
  const h =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return earthRadius * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

async function requestMotionPermissionIfNeeded() {
  return true;
}

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    throw new Error("このブラウザはカメラ取得に対応していません。");
  }

  const constraints = {
    audio: false,
    video: {
      facingMode: { ideal: "environment" },
      width: { ideal: 1280 },
      height: { ideal: 720 },
    },
  };

  const stream = await navigator.mediaDevices.getUserMedia(constraints);
  cameraFeed.srcObject = stream;
  await cameraFeed.play();
}

function getCurrentPosition(options) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("このブラウザはGeolocationに対応していません。"));
      return;
    }

    navigator.geolocation.getCurrentPosition(resolve, reject, options);
  });
}

async function saveCurrentLocationAsHome() {
  saveHomeButton.disabled = true;
  saveHomeButton.textContent = "現在地を取得中...";

  try {
    const position = await getCurrentPosition({
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 15000,
    });

    const homeTarget = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      radiusMeters: DEFAULT_RADIUS_METERS,
      savedAt: new Date().toISOString(),
    };

    window.localStorage.setItem(HOME_STORAGE_KEY, JSON.stringify(homeTarget));
    addSavedHomeTarget();
    statusTitle.textContent = "自宅テスト地点を保存";
    distanceText.textContent = "この端末だけで半径100m表示に使います";
    saveHomeButton.textContent = "自宅テスト地点を保存済み";
  } catch (error) {
    statusTitle.textContent = "自宅保存エラー";
    distanceText.textContent = error.message || "現在地を保存できませんでした";
    saveHomeButton.disabled = false;
    saveHomeButton.textContent = "現在地を自宅テスト地点に保存";
  }
}

function speakArrival(target) {
  if (announcedTargetName === target.name || !("speechSynthesis" in window)) {
    return;
  }

  announcedTargetName = target.name;
  const variant = target.variantLabel || "動物たち";
  const utterance = new SpeechSynthesisUtterance(`${target.name}に到着。${variant}の演奏が始まります。`);
  utterance.lang = "ja-JP";
  utterance.rate = 0.92;
  utterance.pitch = 1.08;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

function setVisible(activeTarget) {
  const desiredKey = activeTarget
    ? `${activeTarget.modelPath}:${modelLoadState[activeTarget.modelPath]}`
    : "none";

  if (desiredKey === visibleStateKey) {
    outside.classList.toggle("hidden", Boolean(activeTarget));
    return;
  }

  visibleStateKey = desiredKey;

  for (const entity of arEntities) {
    entity.setAttribute("visible", false);
  }

  if (activeTarget) {
    const modelPath = `${activeTarget.modelPath}?v=26`;
    const failed = modelLoadState[activeTarget.modelPath] === "error";
    const loaded = modelLoadState[activeTarget.modelPath] === "loaded";

    if (activeModelPath !== activeTarget.modelPath) {
      activeModelPath = activeTarget.modelPath;
      runtimeAnimation = null;
      modelLoadState[activeTarget.modelPath] = "pending";
      stationModel?.setAttribute("gltf-model", modelPath);
    }

    stationModel?.setAttribute("visible", loaded && !failed);
    fallbackStationModel?.setAttribute("visible", failed);
  }

  outside.classList.toggle("hidden", Boolean(activeTarget));
  updatePhotoGuideControls();
}

function hideWebARBackdropNodes(model) {
  const hiddenNameParts = [
    "warm_concert_backdrop",
    "subtle_backdrop_panel",
  ];

  model.traverse((node) => {
    if (!node.name) {
      return;
    }

    if (hiddenNameParts.some((namePart) => node.name.includes(namePart))) {
      node.visible = false;
    }
  });
}

function adjustWebARQuartetLayout(model) {
  model.traverse((node) => {
    if (!node.name) {
      return;
    }

    if (node.name.endsWith("_quartet_player") && node.position.y < 0) {
      const side = node.position.x < 0 ? -1 : 1;
      node.position.x = side * 2.65;
    } else if (node.name.endsWith("_music_stand") && node.position.y < -0.5) {
      const side = node.position.x < 0 ? -1 : 1;
      node.position.x = side * 1.65;
    }
  });
}

function updateByPosition(position) {
  const now = Date.now();
  latestPosition = position;

  if (previewTarget) {
    if (now - lastStatusUpdateMs > 800) {
      updatePreviewStatus();
      lastStatusUpdateMs = now;
    }
    if (activeTarget !== previewTarget) {
      activeTarget = previewTarget;
      setVisible(activeTarget);
    }
    return;
  }

  const { latitude, longitude, accuracy } = position.coords;
  const nearest = TARGETS
    .map((target) => ({
      ...target,
      distance: distanceMeters(latitude, longitude, target.latitude, target.longitude),
    }))
    .sort((a, b) => a.distance - b.distance)[0];

  const roundedDistance = Math.round(nearest.distance);
  const roundedAccuracy = Math.round(accuracy || 0);
  const isInside = nearest.distance <= nearest.radiusMeters;
  const shouldShow = hasLatchedVisibleTarget || isInside;

  if (now - lastStatusUpdateMs > 1500) {
    statusTitle.textContent = shouldShow ? "表示エリア内 / 駅別キャラ v26" : "表示エリア外";
    const variantText = nearest.variantLabel ? ` / ${nearest.variantLabel}` : "";
    distanceText.textContent = `${nearest.name}まで約${roundedDistance}m / GPS精度 約${roundedAccuracy}m${variantText}`;
    outsideDistance.textContent = `${nearest.name}まで約${roundedDistance}mです。半径${nearest.radiusMeters}m以内で表示されます。`;
    lastStatusUpdateMs = now;
  }

  if (isInside && !hasLatchedVisibleTarget) {
    hasLatchedVisibleTarget = true;
    activeTarget = nearest;
    setVisible(activeTarget);
  } else if (!activeTarget && shouldShow) {
    activeTarget = nearest;
    setVisible(activeTarget);
  } else if (!shouldShow) {
    activeTarget = null;
    setVisible(null);
  }

  if (isInside) {
    speakArrival(nearest);
  }
}

function collectRuntimeAnimationNodes(model) {
  hideWebARBackdropNodes(model);
  adjustWebARQuartetLayout(model);

  const state = {
    bows: [],
    winds: [],
    percussion: [],
    heads: [],
    notes: [],
    text: [],
    waves: [],
    bases: new Map(),
  };

  model.traverse((node) => {
    if (!node.name) {
      return;
    }

    if (node.name.includes("_bow_anim")) {
      state.bows.push(node);
    } else if (node.name.includes("_wind_anim")) {
      state.winds.push(node);
    } else if (node.name.includes("_percussion_anim")) {
      state.percussion.push(node);
    } else if (node.name.endsWith("_head")) {
      state.heads.push(node);
    } else if (node.name.includes("_note_")) {
      state.notes.push(node);
    } else if (node.name.includes("dancing_arrival_char") || node.name.includes("announcement_caption")) {
      state.text.push(node);
    } else if (node.name.includes("announcement_sound_wave")) {
      state.waves.push(node);
    }

    state.bases.set(node.uuid, {
      position: node.position.clone(),
      rotation: node.rotation.clone(),
      scale: node.scale.clone(),
    });
  });

  return state;
}

function animateRuntimeNodes(state, seconds) {
  if (!state) {
    return;
  }

  state.bows.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 5.6 + index * 0.7;
    node.position.x = base.position.x + Math.sin(phase) * 0.22;
    node.rotation.y = base.rotation.y + Math.sin(phase) * 0.18;
  });

  state.winds.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 3.2 + index * 0.7;
    node.position.z = base.position.z + Math.sin(phase) * 0.045;
    node.rotation.z = base.rotation.z + Math.sin(phase * 0.75) * 0.055;
  });

  state.percussion.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 6.0 + index * 0.9;
    node.rotation.z = base.rotation.z + Math.sin(phase) * 0.12;
    node.position.z = base.position.z + Math.abs(Math.sin(phase)) * 0.030;
  });

  state.heads.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 2.8 + index * 0.8;
    node.rotation.x = base.rotation.x + Math.sin(phase) * 0.13;
    node.rotation.z = base.rotation.z + Math.sin(phase * 0.75) * 0.05;
  });

  state.notes.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 2.0 + index * 0.9;
    node.position.y = base.position.y + Math.sin(phase) * 0.16;
    node.rotation.z = base.rotation.z + Math.sin(phase) * 0.16;
  });

  state.text.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 3.5 + index * 0.42;
    node.position.y = base.position.y + Math.abs(Math.sin(phase)) * 0.13;
    node.rotation.z = base.rotation.z + Math.sin(phase) * 0.11;
  });

  state.waves.forEach((node, index) => {
    const base = state.bases.get(node.uuid);
    if (!base) return;
    const phase = seconds * 4.0 + index * 0.65;
    const pulse = 1 + Math.abs(Math.sin(phase)) * 0.35;
    node.scale.set(base.scale.x * pulse, base.scale.y * pulse, base.scale.z * pulse);
  });
}

function animateVisibleContent(timeMs) {
  const seconds = timeMs / 1000;

  if (activeTarget) {
    if (stationModel) {
      stationModel.object3D.position.y = -1.25;
      stationModel.object3D.rotation.y = 0;
      applyModelScale();
      animateRuntimeNodes(runtimeAnimation, seconds);
    }

    if (fallbackStationModel) {
      fallbackStationModel.object3D.rotation.z = Math.sin(seconds * 2.4) * 0.035;
    }
  }

  window.requestAnimationFrame(animateVisibleContent);
}

function handleGeoError(error) {
  statusTitle.textContent = "位置情報エラー";
  distanceText.textContent = error.message || "位置情報を取得できませんでした";
  outside.classList.remove("hidden");
  outsideDistance.textContent = "ブラウザ設定で位置情報の許可を確認してください。";
}

async function start() {
  if (started) {
    return;
  }

  started = true;
  startButton.disabled = true;
  startButton.textContent = "起動中...";

  const motionGranted = await requestMotionPermissionIfNeeded();
  if (!motionGranted) {
    statusTitle.textContent = "モーション未許可";
    distanceText.textContent = "iOSではモーション許可が必要です。";
  }

  try {
    await startCamera();
  } catch (error) {
    statusTitle.textContent = "カメラエラー";
    distanceText.textContent = error.message || "カメラを起動できませんでした";
    startButton.disabled = false;
    startButton.textContent = "GPS WebARを開始";
    started = false;
    return;
  }

  gate.classList.add("hidden");
  previewPanel.classList.remove("hidden");
  musicButton?.classList.remove("hidden");
  photoGuidePanel?.classList.remove("hidden");
  activatePreviewTarget(Number(previewStationSelect.value || 0));

  if (!navigator.geolocation) {
    handleGeoError({ message: "このブラウザはGeolocationに対応していません。評価モードは使用できます。" });
    return;
  }

  navigator.geolocation.watchPosition(updateByPosition, handleGeoError, {
    enableHighAccuracy: true,
    maximumAge: 1000,
    timeout: 15000,
  });
}

stationModel?.addEventListener("model-error", () => {
  if (activeModelPath) {
    modelLoadState[activeModelPath] = "error";
  }
  visibleStateKey = "";
  setVisible(activeTarget);
  statusTitle.textContent = "モデル未読込";
  distanceText.textContent = activeModelPath
    ? `GLBを確認してください: ${activeModelPath}`
    : "駅別GLBを確認してください";
});

stationModel?.addEventListener("model-loaded", () => {
  if (activeModelPath) {
    modelLoadState[activeModelPath] = "loaded";
  }
  runtimeAnimation = collectRuntimeAnimationNodes(stationModel.object3D);
  visibleStateKey = "";
  setVisible(activeTarget);
  if (!started) {
    const nodeCount = runtimeAnimation
      ? runtimeAnimation.bows.length +
        runtimeAnimation.winds.length +
        runtimeAnimation.percussion.length +
        runtimeAnimation.heads.length +
        runtimeAnimation.notes.length +
        runtimeAnimation.text.length +
        runtimeAnimation.waves.length
      : 0;
    statusTitle.textContent = `モデル読込済み v26`;
    distanceText.textContent = `アニメ対象 ${nodeCount} 個 / 開始ボタンを押してください`;
  }
});

setupPreviewControls();
previewStationSelect.addEventListener("change", () => {
  activatePreviewTarget(Number(previewStationSelect.value || 0));
});
previewPrev.addEventListener("click", () => {
  activatePreviewTarget(Number(previewStationSelect.value || 0) - 1);
});
previewNext.addEventListener("click", () => {
  activatePreviewTarget(Number(previewStationSelect.value || 0) + 1);
});
gpsModeButton.addEventListener("click", clearPreviewTarget);
musicButton?.addEventListener("click", toggleMusic);
modelSmallerButton?.addEventListener("click", () => adjustModelScale(-1));
modelLargerButton?.addEventListener("click", () => adjustModelScale(1));
childGuideButton?.addEventListener("click", toggleChildGuide);
startButton.addEventListener("click", start);
saveHomeButton.addEventListener("click", saveCurrentLocationAsHome);
updateMusicButton();
updatePhotoGuideControls();
window.requestAnimationFrame(animateVisibleContent);
