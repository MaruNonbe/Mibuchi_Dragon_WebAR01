AFRAME.registerComponent("play-all-model-animations", {
  schema: {
    timeScale: { default: 1.0 },
  },

  init() {
    this.mixer = null;
    this.actions = [];
    this.bows = [];
    this.heads = [];
    this.notes = [];
    this.dancingText = [];
    this.soundWaves = [];
    this.baseTransforms = new Map();

    this.el.addEventListener("model-loaded", (event) => {
      const model = event.detail.model;
      const clips = model.animations || [];

      model.traverse((node) => {
        if (!node.name) {
          return;
        }

        if (node.name.includes("_bow_anim")) {
          this.bows.push(node);
        } else if (node.name.endsWith("_head")) {
          this.heads.push(node);
        } else if (node.name.includes("_note_")) {
          this.notes.push(node);
        } else if (node.name.includes("dancing_arrival_char") || node.name.includes("announcement_caption")) {
          this.dancingText.push(node);
        } else if (node.name.includes("announcement_sound_wave")) {
          this.soundWaves.push(node);
        }

        this.baseTransforms.set(node.uuid, {
          position: node.position.clone(),
          rotation: node.rotation.clone(),
          scale: node.scale.clone(),
        });
      });

      if (!clips.length) {
        this.el.setAttribute("data-animation-count", "0");
      } else {
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
      }

      this.el.setAttribute(
        "data-web-animation-nodes",
        String(this.bows.length + this.heads.length + this.notes.length + this.dancingText.length + this.soundWaves.length),
      );
    });
  },

  tick(time, deltaTime) {
    const seconds = time / 1000;

    if (this.mixer && deltaTime) {
      this.mixer.update((deltaTime / 1000) * this.data.timeScale);
    }

    this.bows.forEach((node, index) => {
      const base = this.baseTransforms.get(node.uuid);
      if (!base) return;
      const phase = seconds * 5.4 + index * 0.65;
      node.position.x = base.position.x + Math.sin(phase) * 0.22;
      node.position.z = base.position.z + Math.cos(phase) * 0.035;
      node.rotation.y = base.rotation.y + Math.sin(phase) * 0.18;
    });

    this.heads.forEach((node, index) => {
      const base = this.baseTransforms.get(node.uuid);
      if (!base) return;
      const phase = seconds * 2.6 + index * 0.8;
      node.rotation.x = base.rotation.x + Math.sin(phase) * 0.12;
      node.rotation.z = base.rotation.z + Math.sin(phase * 0.7) * 0.05;
    });

    this.notes.forEach((node, index) => {
      const base = this.baseTransforms.get(node.uuid);
      if (!base) return;
      const phase = seconds * 1.8 + index * 0.9;
      node.position.y = base.position.y + Math.sin(phase) * 0.16;
      node.rotation.z = base.rotation.z + Math.sin(phase) * 0.15;
    });

    this.dancingText.forEach((node, index) => {
      const base = this.baseTransforms.get(node.uuid);
      if (!base) return;
      const phase = seconds * 3.2 + index * 0.4;
      node.position.y = base.position.y + Math.abs(Math.sin(phase)) * 0.13;
      node.rotation.z = base.rotation.z + Math.sin(phase) * 0.10;
    });

    this.soundWaves.forEach((node, index) => {
      const base = this.baseTransforms.get(node.uuid);
      if (!base) return;
      const phase = seconds * 3.8 + index * 0.6;
      const pulse = 1 + Math.abs(Math.sin(phase)) * 0.35;
      node.scale.set(base.scale.x * pulse, base.scale.y * pulse, base.scale.z * pulse);
    });
  },
});
