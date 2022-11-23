<template>
  <a-row class="file-toolbar" :style="{'--marginleft': marginLeft}">
    <a-col :span="20">
      <a @click="goto({ type: 'home' }, $event)">
        <a-icon type="home" />{{ $t("all.home") }}
      </a>
      <a-divider type="vertical" />
      <a
        :disabled="current_dir.id == 0"
        @click="goto({ type: 'back' }, $event)"
      >
        <a-icon type="rollback" />{{ $t("all.back") }}
      </a>
      <a-divider type="vertical" />
      <span class="dirname">{{ current_dir.name }}</span>
    </a-col>
    <a-col :span="4">
      <!-- Switch view -->
      <a class="float-right" @click="switchFileView">
        <a-icon
          v-if="file_view == 'grid'"
          type="unordered-list"
          :style="{ fontSize: '16px' }"
        />
        <a-icon
          v-else-if="file_view == 'list'"
          type="appstore"
          :style="{ fontSize: '16px' }"
        />
      </a>
    </a-col>
  </a-row>
</template>

<script>
export default {
  computed: {
    marginLeft() {
      return this.file_view == 'grid' ? "60px" : "0px";
    },
  },
  methods: {
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    switchFileView(e) {
      this.$emit("switch-file-view", e);
    },
  },
  props: ["current_dir", "file_view"],
};
</script>

<style>

.float-right {
  float: right;
  background-color: white;
}

.file-toolbar {
  float: right;
  width: calc(100% - var(--marginleft));
}

.file-toolbar .ant-col {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.file-toolbar .ant-divider {
  margin: 0 3px;
}

</style>