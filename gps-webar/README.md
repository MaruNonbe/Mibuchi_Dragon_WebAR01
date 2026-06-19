# 長井駅到着 GPS WebAR

長井駅のGPS位置から半径100m以内で、動物弦楽四重奏モデルを表示するWebARページです。

## 表示位置

- 対象: 山形鉄道フラワー長井線 長井駅
- 緯度: `38.106518`
- 経度: `140.033583`
- 表示半径: `100m`

座標は Wikipedia の Nagai Station (Yamagata) ページに掲載されている座標を使用しています。

## 検証用GPS

長井駅以外に、検証用としてタスパークホテル長井のGPSも追加しています。

- 対象: タスパークホテル長井 検証地点
- 緯度: `38.1013040`
- 経度: `140.0433785`
- 表示半径: `100m`

座標は OpenStreetMap / Overpass API の `タス・パーク・ホテル` POI を使用しています。

## ファイル構成

- `index.html`: GPS WebARページ
- `main.js`: 100m判定、アナウンス、表示制御
- `styles.css`: スマホ向けUI
- `assets/nagai_station_quartet.glb`: Blenderから書き出されるモデル

## アニメーション

GLB内のアニメーション再生には `aframe-extras` の `animation-mixer` を使用しています。
`index.html` でCDNから読み込んでいるため、公開時はインターネット接続が必要です。

## GLBを書き出す

Blenderで次を実行します。

```bash
blender --python ../create_animal_string_quartet.py
```

実行すると、次のファイルが自動生成されます。

```text
gps-webar/assets/nagai_station_quartet.glb
```

BlenderのText Editorからスクリプトを実行する場合も、同じ場所に書き出されます。

## 公開条件

iOS / Android の実機では、次が必要です。

- HTTPSで公開すること
- カメラ許可
- 位置情報許可
- iOSではモーション/方位の許可

ローカルPCの `file://` ではカメラやGPSが動かないことがあります。GitHub Pages、Netlify、Firebase Hostingなど、HTTPSで配信できる場所に `gps-webar` フォルダを配置してください。

## テスト

長井駅から100m以内:

- 「長井駅到着」のアナウンス
- 動物弦楽四重奏モデル表示

100mより外:

- 距離表示のみ
- モデル非表示

GPS精度が悪い場合、100m以内でも一時的に表示されないことがあります。駅構内や屋外で数秒待つと安定しやすいです。
