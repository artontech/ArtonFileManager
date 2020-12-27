<template>
  <a-dropdown :trigger="trigger">
    <slot></slot>

    <!-- Menu -->
    <a-menu slot="overlay">
      <a-menu-item key="download" @click="download(item, $event)">
        <a-icon type="download" />
        {{$t('all.download')}}
      </a-menu-item>
      <a-menu-item v-if="item.type == 'dir'" key="open" @click="goto(item, $event)">
        <a-icon type="arrow-right" />
        {{$t('all.open')}}
      </a-menu-item>

      <!-- * * * * * * * * Start: Submenu * * * * * * * * -->
      <a-sub-menu key="edit">
        <span slot="title" class="title">
          <a-icon type="edit" />
          {{$t('all.edit')}}
        </span>
        <a-menu-item key="tag" @click="addTag(item, $event)">
          <a-icon type="tag" />
          {{$t('all.edit')+$t('all.tag')}}
        </a-menu-item>
        <a-menu-item key="moveto" @click="moveto(item, $event)">
          <a-icon type="export" />
          {{$t('all.move_to')}}
        </a-menu-item>
        <a-menu-item key="rename" @click="rename(item, $event)">
          <a-icon type="form" />
          {{$t('all.rename')}}
        </a-menu-item>
        <a-menu-divider />
        <a-menu-item key="del" @click="del(item, $event)">
          <a-icon type="delete" />
          {{$t('all.delete')}}
        </a-menu-item>
      </a-sub-menu>
      <!-- * * * * * * * * End: Submenu * * * * * * * * -->

      <a-menu-divider />

      <a-menu-item key="detail" @click="detail(item, $event)">
        <a-icon type="info-circle" />
        {{$t('all.detail')}}
      </a-menu-item>
    </a-menu>
  </a-dropdown>
</template>

<script>
export default {
  name: "DropdownMenu",
  props: ["trigger", "item"],
  data() {
    return {};
  },
  created() {},
  beforeMount() {},
  beforeUpdate() {},
  methods: {
    addTag(target, event) {
      this.$emit("add-tag", target, event);
    },
    del(target, event) {
      this.$emit("del", target, event);
    },
    detail(target, event) {
      const vm = this;
      vm.$emit(
        "detail",
        vm.item.type == "file" ? vm.item.attribute : vm.item.id,
        vm.item.type,
        event
      );
    },
    download(target, event) {
      this.$emit("download", target, event);
    },
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    moveto(target, event) {
      this.$emit("moveto", target, event);
    },
    rename(target, event) {
      this.$emit("rename", target, event);
    }
  }
};
</script>

<style scoped>
.title {
  margin-right: 10px;
}
</style>