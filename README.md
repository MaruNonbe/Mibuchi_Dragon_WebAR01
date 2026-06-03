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
