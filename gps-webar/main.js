const TARGETS = [
  {
    name: "長井駅",
    latitude: 38.106518,
    longitude: 140.033583,
    radiusMeters: 100,
    modelId: "quartetStation",
    fallbackId: "fallbackStation",
  },
  {
    name: "タスパークホテル長井 検証地点",
    latitude: 38.1013040,
    longitude: 140.0433785,
    radiusMeters: 100,
    modelId: "quartetHotelTest",
    fallbackId: "fallbackHotelTest",
  },
];

const gate = document.getElementById("gate");
const startButton = document.getElementById("startButton");
const statusTitle = document.getElementById("statusTitle");
const distanceText = document.getElementById("distanceText");
const outside = document.getElementById("outside");
const outsideDistance = document.getElementById("outsideDistance");
const cameraFeed = document.getElementById("cameraFeed");
const arEntities = TARGETS.flatMap((target) => [
  document.getElementById(target.modelId),
  document.getElementById(target.fallbackId),
]).filter(Boolean);

let announced = false;
let started = false;
let activeTarget = null;
let visibleStateKey = "";
let hasLatchedVisibleTarget = false;
let lastStatusUpdateMs = 0;

const runtimeAnimation = {
  quartetStation: null,
  quartetHotelTest: null,
};

const modelLoadState = {
  quartetStation: "pending",
  quartetHotelTest: "pending",
};

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

function speakArrival(targetName) {
  if (announced || !("speechSynthesis" in window)) {
    return;
  }

  announced = true;
  const utterance = new SpeechSynthesisUtterance(`${targetName}に到着。動物たちの演奏が始まります。`);
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
    statusTitle.textContent = shouldShow ? "表示エリア内 / 安定表示 v16" : "表示エリア外";
    distanceText.textContent = `${nearest.name}まで約${roundedDistance}m / GPS精度 約${roundedAccuracy}m`;
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
    speakArrival(nearest.name);
  }
}

function collectRuntimeAnimationNodes(model) {
  hideWebARBackdropNodes(model);

  const state = {
    bows: [],
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

for (const target of TARGETS) {
  const model = document.getElementById(target.modelId);
  model?.addEventListener("model-error", () => {
    modelLoadState[target.modelId] = "error";
    visibleStateKey = "";
    setVisible(activeTarget);
    statusTitle.textContent = "モデル未読込";
    distanceText.textContent = "GLBを書き出してください: gps-webar/assets/nagai_station_quartet.glb";
  });

  model?.addEventListener("model-loaded", () => {
    modelLoadState[target.modelId] = "loaded";
    runtimeAnimation[target.modelId] = collectRuntimeAnimationNodes(model.object3D);
    visibleStateKey = "";
    setVisible(activeTarget);
    if (!started) {
      const nodeCount = runtimeAnimation[target.modelId]
        ? runtimeAnimation[target.modelId].bows.length +
          runtimeAnimation[target.modelId].heads.length +
          runtimeAnimation[target.modelId].notes.length +
          runtimeAnimation[target.modelId].text.length +
          runtimeAnimation[target.modelId].waves.length
        : 0;
      statusTitle.textContent = `モデル読込済み v8`;
      distanceText.textContent = `アニメ対象 ${nodeCount} 個 / 開始ボタンを押してください`;
    }
  });
}

startButton.addEventListener("click", start);
window.requestAnimationFrame(animateVisibleContent);
