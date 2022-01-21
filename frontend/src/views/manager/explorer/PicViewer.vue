<template>
  <div :id="id">
    <!-- <img class="image" :alt="alt" :src="src" /> -->
  </div>
</template>

<script>
import Konva from "konva";
// by default Konva prevent some events when node is dragging
// it improve the performance and work well for 95% of cases
// we need to enable all events on Konva, even when we are dragging a node
// so it triggers touchmove correctly
Konva.hitOnDragEnabled = true;
var lastCenter = null;
var lastDist = 0;

export default {
  data() {
    return {
      repository: null,
      setting: null,
      stage: null,
      layer: null,
      width: 0,
      height: 0,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    if (!vm.repository.wid) {
      return;
    }
  },
  computed: {
  },
  methods: {
    init() {
      const vm = this;
      const container = document.getElementById(vm.id);
      if (!container) return;
      vm.width = container.clientWidth,
      vm.height = container.clientHeight;

      if (!vm.stage) {
        vm.stage = new Konva.Stage({
          container: vm.id,
          draggable: true,
        });
        vm.stage.on('touchmove', vm.onTouchMove);
        vm.stage.on('touchend', () => {
          lastDist = 0;
          lastCenter = null;
        });
        vm.stage.on("wheel", vm.onWheel);
      }
      vm.stage.width(vm.width);
      vm.stage.height(vm.height);

      if (!vm.layer) {
        vm.layer = new Konva.Layer({
          id: "konva-layer",
        });
        vm.stage.add(vm.layer);
      }

      Konva.Image.fromURL(
        vm.src,
        (img) => {
          img.setAttrs({
            width: img.naturalWidth,
            height: img.naturalHeight,
            x: 0,
            y: 0,
            draggable: true,
          });
          vm.layer.add(img);
          vm.rescalePicture();
        }
      );
    },
    onClose() {
      const vm = this;
      if (vm.layer) {
        vm.layer.destroyChildren();
      }
    },
    onTouchMove(e) {
      function getDistance(p1, p2) {
        return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
      }

      function getCenter(p1, p2) {
        return {
          x: (p1.x + p2.x) / 2,
          y: (p1.y + p2.y) / 2,
        };
      }

      const vm = this;
      e.evt.preventDefault();
      const touch1 = e.evt.touches[0],
        touch2 = e.evt.touches[1];
      if (!touch1 || !touch2 || !vm.stage) return;

      // if the stage was under Konva's drag&drop
      // we need to stop it, and implement our own pan logic with two pointers
      if (vm.stage.isDragging()) {
        vm.stage.stopDrag();
      }

      const p1 = {
        x: touch1.clientX,
        y: touch1.clientY,
      };
      const p2 = {
        x: touch2.clientX,
        y: touch2.clientY,
      };

      if (!lastCenter) {
        lastCenter = getCenter(p1, p2);
        return;
      }
      const newCenter = getCenter(p1, p2);

      const dist = getDistance(p1, p2);

      if (!lastDist) {
        lastDist = dist;
      }

      // local coordinates of center point
      const pointTo = {
        x: (newCenter.x - vm.stage.x()) / vm.stage.scaleX(),
        y: (newCenter.y - vm.stage.y()) / vm.stage.scaleX(),
      };

      const scale = vm.stage.scaleX() * (dist / lastDist);

      vm.stage.scaleX(scale);
      vm.stage.scaleY(scale);

      // calculate new position of the stage
      const dx = newCenter.x - lastCenter.x;
      const dy = newCenter.y - lastCenter.y;

      const newPos = {
        x: newCenter.x - pointTo.x * scale + dx,
        y: newCenter.y - pointTo.y * scale + dy,
      };

      vm.stage.position(newPos);

      lastCenter = newCenter;
      lastDist = dist;
    },
    onWheel(e) {
      const vm = this;
      e.evt.preventDefault();
      const scale = e.evt.wheelDelta > 0 ? 1.05 : 1 / 1.05,
        scaleX = vm.stage.scaleX() * scale,
        scaleY = vm.stage.scaleY() * scale;
      const pointer = vm.stage.getPointerPosition();
      if (!pointer) return;
      const mousePointTo = {
        x: (pointer.x - vm.stage.x()) / vm.stage.scaleX(),
        y: (pointer.y - vm.stage.y()) / vm.stage.scaleY(),
      };
      const newPos = {
        x: pointer.x - mousePointTo.x * scaleX,
        y: pointer.y - mousePointTo.y * scaleY,
      };

      vm.stage.scaleX(scaleX);
      vm.stage.scaleY(scaleY);
      vm.stage.position(newPos);
    },
    rescalePicture() {
      const vm = this;
      if (!vm.stage) {
        console.log(`${vm.id} rescalePicture failed, no stage`);
        return false;
      }
      vm.stage.x(0);
      vm.stage.y(0);
      vm.stage.scaleX(1);
      vm.stage.scaleY(1);
      return true;
    },
  },
  mounted() {
  },
  props: [
    "alt",
    "id",
    "src",
  ],
}
</script>

<style>

</style>