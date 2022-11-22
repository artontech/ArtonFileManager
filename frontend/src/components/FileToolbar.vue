<template>
  <span class="file-toolbar">
    <a @click="goto({ type: 'home' }, $event)">
      <a-icon type="home" />{{ $t("all.home") }}
    </a>
    <a-divider type="vertical" />
    <a :disabled="current_dir.id==0" @click="goto({ type: 'back' }, $event)">
      <a-icon type="rollback" />{{ $t("all.back") }}
    </a>
    <a-divider type="vertical" />
    <span>{{ current_dir.name }}</span>

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
  </span>
</template>

<script>
export default {
  methods: {
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    switchFileView(e) {
      this.$emit("switch-file-view", e);
    },
  },
  props: [
    "current_dir",
    "file_view",
  ],
};
</script>

<style>

.float-right {
  float: right;
}

</style>