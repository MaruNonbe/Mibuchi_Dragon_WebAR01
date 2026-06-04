# Mibuchi Dragon WebAR

三淵渓谷VR龍演出を、スマートフォンブラウザ向けWebARとして確認するための最小構成です。

## フォルダー構成

```text
Mibuchi_Dragon_WebAR/
├─ index.html
├─ README.md
└─ assets/
   ├─ dragon_web.glb
   ├─ dragon_web.usdz
   ├─ dragon_web_sky.glb
   ├─ dragon_web_sky.usdz
   ├─ dragon_web_flight.glb
   ├─ dragon_web_flight.usdz
   ├─ dragon_web_giant_approach.glb
   ├─ dragon_web_giant_approach.usdz
   ├─ audio/
   │  ├─ dragon_flight.mp3
   │  └─ dragon_flight.wav
   ├─ images/
   │  └─ thumbnail.jpg
   └─ source/
      ├─ dragon_source.fbx
      ├─ dragon_web.glb
      └─ dragon_web_original_before_webar_anim.glb
```

## アニメーション確認

`assets/source/dragon_web.glb` には `Scene` アニメーションが含まれていました。

WebAR表示で確実に動きが分かるように、`assets/dragon_web.glb` には追加で `Idle_S_Curve_Loop` を入れています。

追加アニメーションの内容:

- spine_00 から spine_11 に左右S字のうねり
- head に軽い上下動
- tail_tip にゆっくりした揺れ
- 4秒ループ
- model-viewer 側で `animation-name="Idle_S_Curve_Loop"` を明示指定

ブラウザの開発者コンソールには、読み込み時に以下のログが出ます。

```text
[WEBAR_ANIMATIONS] ["Scene", "Idle_S_Curve_Loop"]
```

## 空中表示版

ARビューアは床面にモデルを配置するため、空中表示版ではモデル内部で龍本体を上方向へ移動しています。

現在の `index.html` は以下を参照します。

```html
src="assets/dragon_web_sky.glb"
ios-src="assets/dragon_web_sky.usdz"
ar-placement="floor"
ar-scale="fixed"
```

空中表示版の内容:

- 龍本体の高さ: 3.2m
- 床面付近: `FloorShadowAnchor` の薄い影
- GLB animation: `Idle_S_Curve_Loop`, `Scene`
- USDZ animation: `SkelAnimation` あり
- USDZ rotations time samples: 97

## 飛行ルート版

現在の `index.html` は、ページ上のボタンで飛行ルート版と巨大龍版を切り替えられます。

```html
src="assets/dragon_web_flight.glb"
ios-src="assets/dragon_web_flight.usdz"
ar-placement="floor"
ar-scale="fixed"
animation-name="Flight_Loop_12s"
```

飛行ルート版の内容:

- animation: `Flight_Loop_12s`
- duration: 12秒
- frame range: 0-288
- fps: 24
- 高さ: 約2.88m〜3.82m
- 横幅: 約5.2m
- 奥行き: 約3.4m
- 床面付近: `FlightFloorShadowAnchor` の薄い影
- 龍本体: 空中を楕円状に旋回し、前方上空を横切って戻る
- spine_00〜spine_11、head、tail_tipのうねりを同じアニメーション内に焼き込み
- USDZ: `SkelAnimation` あり、root translate/rotate と bone rotations に289サンプル

## 巨大龍版

`巨大な龍` ボタンを押すと、以下のモデルへ切り替わります。

```html
src="assets/dragon_web_giant_approach.glb"
ios-src="assets/dragon_web_giant_approach.usdz"
```

巨大龍版の内容:

- iPhone AR Quick Look: `dragon_web_giant_approach.usdz`
- Android / ページ内3D: `dragon_web_giant_approach.glb`
- animation: `Giant_Approach_Overhead_Circle`
- duration: 16秒
- scale: 2.8倍
- start: 遠方約15m、高さ約6.2m
- overhead: 前方上空約4.15m、最短距離約4.35m
- finish: 上空約7mで旋回
- ひげ離れ対策: head / spine / whisker ボーンは個別回転させず、Armature全体のルート移動で飛行
- 飛行アニメーション付きモデルは `飛行する龍` ボタンで選択

## iOS Safari

1. GitHub PagesなどHTTPSで公開します。
2. iPhone SafariでURLを開きます。
3. ページ上の3D表示では `dragon_web.glb` のアニメーションを確認できます。
4. `ARで龍を見る` を押すと、Quick Lookで `dragon_web.usdz` が開きます。

注意: iOSのAR Quick Lookは `dragon_web.usdz` を使います。現在の `assets/dragon_web.usdz` は、Blender 5.0で `assets/dragon_web.glb` の `Idle_S_Curve_Loop` を選択して再生成したアニメーション付きUSDZです。

USDZ検査結果:

- `SkelRoot`: 1
- `Skeleton`: 1
- `SkelAnimation`: 1
- `rotations` time samples: 97
- frame range: 0-96
- fps: 24

## Android Chrome

1. GitHub PagesなどHTTPSで公開します。
2. Android ChromeでURLを開きます。
3. ページ上の3D表示では `dragon_web.glb` のアニメーションを確認できます。
4. `ARで龍を見る` を押すと、Scene Viewer / WebXR経由で `dragon_web.glb` が開きます。

## GitHub Pages公開手順

1. GitHubで新しいRepositoryを作成します。
2. `Mibuchi_Dragon_WebAR` の中身をRepository直下に配置します。
3. `assets/dragon_web.glb` と `assets/dragon_web.usdz` を含めます。
4. `Settings > Pages` を開きます。
5. Sourceを `Deploy from a branch` にします。
6. Branchを `main`、Folderを `/root` にします。
7. 発行URLをQRコード化します。

## 次の段階

Unityの `BakedPathAsset` はGLBには入りません。飛行ルート、水面、水しぶきまで含める場合は、次にThree.js版として以下を実装します。

- Three.jsで `dragon_web.glb` を読み込み
- JavaScriptのSplineで飛行ルートを再現
- 水面を軽量Plane + alpha textureで表現
- 水しぶき・水滴を少数Billboard Particleで表現
- 龍のS字うねりはGLBアニメーションまたはThree.js側のbone制御で再現
