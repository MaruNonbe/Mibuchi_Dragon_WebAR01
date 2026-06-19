const TARGET = {
  name: "長井駅",
  latitude: 38.106518,
  longitude: 140.033583,
  radiusMeters: 100,
};

const gate = document.getElementById("gate");
const startButton = document.getElementById("startButton");
const statusTitle = document.getElementById("statusTitle");
const distanceText = document.getElementById("distanceText");
const outside = document.getElementById("outside");
const outsideDistance = document.getElementById("outsideDistance");
const quartet = document.getElementById("nagaiQuartet");
const fallbackSign = document.getElementById("fallbackSign");

let announced = false;
let started = false;

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

function speakArrival() {
  if (announced || !("speechSynthesis" in window)) {
    return;
  }

  announced = true;
  const utterance = new SpeechSynthesisUtterance("長井駅到着。動物たちの演奏が始まります。");
  utterance.lang = "ja-JP";
  utterance.rate = 0.92;
  utterance.pitch = 1.08;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

function setVisible(isVisible) {
  quartet.setAttribute("visible", isVisible);
  fallbackSign.setAttribute("visible", isVisible);
  outside.classList.toggle("hidden", isVisible);
}

function updateByPosition(position) {
  const { latitude, longitude, accuracy } = position.coords;
  const distance = distanceMeters(latitude, longitude, TARGET.latitude, TARGET.longitude);
  const roundedDistance = Math.round(distance);
  const roundedAccuracy = Math.round(accuracy || 0);
  const isInside = distance <= TARGET.radiusMeters;

  statusTitle.textContent = isInside ? "表示エリア内" : "表示エリア外";
  distanceText.textContent = `${TARGET.name}まで約${roundedDistance}m / GPS精度 約${roundedAccuracy}m`;
  outsideDistance.textContent = `${TARGET.name}まで約${roundedDistance}mです。半径${TARGET.radiusMeters}m以内で表示されます。`;

  setVisible(isInside);
  if (isInside) {
    speakArrival();
  }
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

quartet.addEventListener("model-error", () => {
  statusTitle.textContent = "モデル未読込";
  distanceText.textContent = "GLBを書き出してください: gps-webar/assets/nagai_station_quartet.glb";
});

quartet.addEventListener("model-loaded", () => {
  if (!started) {
    statusTitle.textContent = "モデル読込済み";
    distanceText.textContent = "開始ボタンを押してください";
  }
});

startButton.addEventListener("click", start);
