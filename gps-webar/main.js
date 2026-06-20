const HOME_STORAGE_KEY = "nagaiQuartetHomeTarget";
const DEFAULT_RADIUS_METERS = 100;

const MODEL_DEFINITIONS = {
  strings: {
    modelId: "quartetStrings",
    fallbackId: "fallbackStrings",
    assetPath: "gps-webar/assets/nagai_station_strings.glb",
  },
  winds: {
    modelId: "quartetWinds",
    fallbackId: "fallbackWinds",
    assetPath: "gps-webar/assets/nagai_station_winds.glb",
  },
  percussion: {
    modelId: "quartetPercussion",
    fallbackId: "fallbackPercussion",
    assetPath: "gps-webar/assets/nagai_station_percussion.glb",
  },
};

const ENSEMBLE_MODEL_KEY = {
  strings: "strings",
  woodwinds: "winds",
  brass: "winds",
  percussion: "percussion",
  jazz: "winds",
  taiko: "percussion",
  flute: "winds",
  "low-brass": "winds",
  clarinet: "winds",
  piccolo: "winds",
  sax: "winds",
  handbell: "percussion",
  horn: "winds",
  marimba: "percussion",
  trombone: "winds",
  finale: "percussion",
  test: "strings",
  "home-test": "strings",
};

const STATION_VARIANTS = [
  { variantLabel: "きつねとウサギの弦楽四重奏", ensemble: "strings" },
  { variantLabel: "ネコたちの木管アンサンブル", ensemble: "woodwinds" },
  { variantLabel: "イヌたちの金管ファンファーレ", ensemble: "brass" },
  { variantLabel: "リスたちの打楽器パレード", ensemble: "percussion" },
  { variantLabel: "パンダとペンギンの駅前ジャズ", ensemble: "jazz" },
  { variantLabel: "タヌキたちの和太鼓リズム", ensemble: "taiko" },
  { variantLabel: "シカたちのフルート合奏", ensemble: "flute" },
  { variantLabel: "クマたちの低音ブラス", ensemble: "low-brass" },
  { variantLabel: "ウサギたちのクラリネット隊", ensemble: "clarinet" },
  { variantLabel: "どうぶつ弦楽四重奏", ensemble: "strings" },
  { variantLabel: "小鳥たちのピッコロ行進曲", ensemble: "piccolo" },
  { variantLabel: "キツネたちのサックスバンド", ensemble: "sax" },
  { variantLabel: "白ウサギのハンドベル隊", ensemble: "handbell" },
  { variantLabel: "カモシカたちのホルン合奏", ensemble: "horn" },
  { variantLabel: "カエルたちのマリンバ隊", ensemble: "marimba" },
  { variantLabel: "ヒツジたちのトロンボーン隊", ensemble: "trombone" },
  { variantLabel: "全員集合フィナーレ", ensemble: "finale" },
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
    ...MODEL_DEFINITIONS[ENSEMBLE_MODEL_KEY[STATION_VARIANTS[index % STATION_VARIANTS.length].ensemble]],
    radiusMeters: DEFAULT_RADIUS_METERS,
  })),
  {
    name: "タスパークホテル長井 検証地点",
    latitude: 38.1013040,
    longitude: 140.0433785,
    radiusMeters: DEFAULT_RADIUS_METERS,
    ...MODEL_DEFINITIONS.strings,
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
const arEntities = Object.values(MODEL_DEFINITIONS).flatMap((definition) => [
  document.getElementById(definition.modelId),
  document.getElementById(definition.fallbackId),
]).filter(Boolean);

let announcedTargetName = "";
let started = false;
let activeTarget = null;
let visibleStateKey = "";
let hasLatchedVisibleTarget = false;
let lastStatusUpdateMs = 0;

const runtimeAnimation = {
  quartetStrings: null,
  quartetWinds: null,
  quartetPercussion: null,
};

const modelLoadState = {
  quartetStrings: "pending",
  quartetWinds: "pending",
  quartetPercussion: "pending",
};

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
      ...MODEL_DEFINITIONS.strings,
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
  const deviceOrientation = window.DeviceOrientationEvent;
  if (!deviceOrientation || typeof deviceOrientation.requestPermission !== "function") {
    return true;
  }

  try {
    const result = await deviceOrientation.requestPermission();
    return result === "granted";
  } catch {
    return false;
  }
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
    ? `${activeTarget.modelId}:${modelLoadState[activeTarget.modelId]}`
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
    const model = document.getElementById(activeTarget.modelId);
    const fallback = document.getElementById(activeTarget.fallbackId);
    const failed = modelLoadState[activeTarget.modelId] === "error";

    model?.setAttribute("visible", !failed);
    fallback?.setAttribute("visible", failed);
  }

  outside.classList.toggle("hidden", Boolean(activeTarget));
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
    statusTitle.textContent = shouldShow ? "表示エリア内 / 駅別モデル v21" : "表示エリア外";
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
    const modelEntity = document.getElementById(activeTarget.modelId);
    const fallbackEntity = document.getElementById(activeTarget.fallbackId);

    if (modelEntity) {
      modelEntity.object3D.position.y = -1.25;
      modelEntity.object3D.rotation.y = 0;
      animateRuntimeNodes(runtimeAnimation[activeTarget.modelId], seconds);
    }

    if (fallbackEntity) {
      fallbackEntity.object3D.rotation.z = Math.sin(seconds * 2.4) * 0.035;
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

  if (!navigator.geolocation) {
    handleGeoError({ message: "このブラウザはGeolocationに対応していません。" });
    return;
  }

  gate.classList.add("hidden");
  navigator.geolocation.watchPosition(updateByPosition, handleGeoError, {
    enableHighAccuracy: true,
    maximumAge: 1000,
    timeout: 15000,
  });
}

for (const definition of Object.values(MODEL_DEFINITIONS)) {
  const model = document.getElementById(definition.modelId);
  model?.addEventListener("model-error", () => {
    modelLoadState[definition.modelId] = "error";
    visibleStateKey = "";
    setVisible(activeTarget);
    statusTitle.textContent = "モデル未読込";
    distanceText.textContent = `GLBを書き出してください: ${definition.assetPath}`;
  });

  model?.addEventListener("model-loaded", () => {
    modelLoadState[definition.modelId] = "loaded";
    runtimeAnimation[definition.modelId] = collectRuntimeAnimationNodes(model.object3D);
    visibleStateKey = "";
    setVisible(activeTarget);
    if (!started) {
      const animationState = runtimeAnimation[definition.modelId];
      const nodeCount = animationState
        ? animationState.bows.length +
          animationState.winds.length +
          animationState.percussion.length +
          animationState.heads.length +
          animationState.notes.length +
          animationState.text.length +
          animationState.waves.length
        : 0;
      statusTitle.textContent = `モデル読込済み v21`;
      distanceText.textContent = `アニメ対象 ${nodeCount} 個 / 開始ボタンを押してください`;
    }
  });
}

startButton.addEventListener("click", start);
saveHomeButton.addEventListener("click", saveCurrentLocationAsHome);
window.requestAnimationFrame(animateVisibleContent);
