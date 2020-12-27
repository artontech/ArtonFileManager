<template>
  <a-modal
    v-model="visible"
    :title="title"
    :ok-text="$t('all.ok')"
    :cancel-text="$t('all.cancel')"
    @ok="onOK"
  >
    <a-input :placeholder="placeholder" v-model="value" />
  </a-modal>
</template>

<script>
export default {
  name: "InputBox",
  props: [],
  data() {
    return {
      title: "",
      placeholder: "",
      value: null,
      ok_callback: undefined,
      visible: false
    };
  },
  created() {},
  beforeMount() {},
  beforeUpdate() {},
  methods: {
    initShow(title, placeholder, default_value, ok_callback) {
      const vm = this;
      vm.title = title;
      vm.placeholder = placeholder;
      vm.value = default_value;
      vm.ok_callback = ok_callback;
      vm.visible = true;
    },
    onOK(event) {
      const vm = this;
      if (vm.ok_callback) vm.ok_callback(vm.value, event);
      vm.visible = false;
    }
  }
};
</script>

<style scoped>
</style>