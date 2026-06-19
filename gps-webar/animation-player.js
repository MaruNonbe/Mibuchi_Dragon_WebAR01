AFRAME.registerComponent("play-all-model-animations", {
  schema: {
    timeScale: { default: 1.0 },
  },

  init() {
    this.mixer = null;
    this.actions = [];

    this.el.addEventListener("model-loaded", (event) => {
      const model = event.detail.model;
      const clips = model.animations || [];

      if (!clips.length) {
        this.el.setAttribute("data-animation-count", "0");
        return;
      }

      this.mixer = new THREE.AnimationMixer(model);
      this.actions = clips.map((clip) => {
        const action = this.mixer.clipAction(clip);
        action.reset();
        action.setLoop(THREE.LoopRepeat, Infinity);
        action.clampWhenFinished = false;
        action.enabled = true;
        action.play();
        return action;
      });

      this.el.setAttribute("data-animation-count", String(clips.length));
    });
  },

  tick(_time, deltaTime) {
    if (!this.mixer || !deltaTime) {
      return;
    }

    this.mixer.update((deltaTime / 1000) * this.data.timeScale);
  },
});
