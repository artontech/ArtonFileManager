<template>
  <a-drawer
    placement="right"
    :closable="true"
    :maskClosable="false"
    :title="$t('explorer.tag_drawer.title')"
    :visible="visible"
    :after-visible-change="afterVisibleChange"
    @close="onClose"
  >
    <a-select
      mode="tags"
      v-model="tag_value"
      :style="{ width: '100%', height: '200px' }"
      :defaultValue="tags"
      :dropdownMatchSelectWidth="false"
      :placeholder="$t('explorer.tag_drawer.select1_placeholder')"
      :open="show_select"
      @change="select1Change"
    >
      <a-select-option
        v-for="tag in tag_list"
        :key="tag"
        :default-value="tags"
        >{{ tag }}</a-select-option
      >
    </a-select>

    <!-- Button -->
    <div id="btn-wrapper">
      <a-button type="primary" @click="btn1Click">{{
        $t("all.done")
      }}</a-button>
    </div>
  </a-drawer>
</template>

<script>
import options from "@/config/request";

export default {
  data() {
    return {
      repository: null,
      setting: null,
      tag_list: [],
      tags: [],
      tag_target: [],
      tag_value: [],
      show_select: null,
      mod: false,
      target: null,
      type: null,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    vm.init();
  },
  props: ["visible"],
  methods: {
    init(target) {
      const vm = this;
      vm.show_select = null;
      vm.mod = false;

      // load tags
      vm.tags.splice(0, vm.tags.length);
      vm.tag_target.splice(0, vm.tag_target.length);
      vm.tag_value.splice(0, vm.tag_value.length);
      if (target != undefined) {
        vm.target = target.type == "dir" ? target.id : target.attribute;
        vm.type = target.type;
        for (let i in target.tags) {
          const tag = `${target.tags[i].key}:${target.tags[i].value}`;
          vm.tags.push(tag);
          vm.tag_target.push(target.tags[i]);
          vm.tag_value.push(tag);
        }
      }
    },
    afterVisibleChange(val) {},
    onClose() {
      const vm = this;
      vm.show_select = false;
      vm.tags.splice(0, vm.tags.length);
      vm.$emit("on-close", vm.mod);
    },
    tagDiff(arr1, arr2) {
      const result = { tag: null, key: null, value: null, i: null };
      for (let i in arr1) {
        let tag = arr1[i];
        if (arr2.indexOf(tag) < 0) {
          let sp = tag.split(":");
          result.tag = tag;
          result.key = sp[0];
          result.value = sp[1];
          result.i = i;
          break;
        }
      }
      return result;
    },
    select1Change(value) {
      const vm = this;
      if (value.length > vm.tags.length) {
        // add
        const diff = vm.tagDiff(value, vm.tags);
        vm.addTag(diff.key, diff.value);
      } else if (value.length < vm.tags.length) {
        // delete
        const diff = vm.tagDiff(vm.tags, value);
        vm.updateTag(diff.i, null, null, 1);
      } else {
        // update
        const diff1 = vm.tagDiff(vm.tags, value);
        const diff2 = vm.tagDiff(value, vm.tags);
      }
    },
    btn1Click(e) {
      const vm = this;
      vm.onClose();
    },
    addTag(key, value) {
      const vm = this;
      vm.mod = true; // Add mod flag

      const body = {
        wid: vm.repository.wid,
        target: vm.target,
        type: vm.type,
        key,
        value,
      };
      const onError = () => {
        console.log(`[Error] failed to update tag ${body.path}`);
      };
      vm.$http.post(`http://${vm.setting.address}/tag/add`, body, options).then(
        (resp) => {
          vm.btn1_loading = false;
          if (resp.body.status === "success") {
            // vm.onClose();
            const target = resp.body.data;
            const tag = `${target.key}:${target.value}`;
            vm.tags.push(tag);
            vm.tag_target.push(target);
          } else {
            onError();
          }
        },
        (error) => {
          onError();
        }
      );
    },
    updateTag(id, key, value, delete_id) {
      const vm = this;
      vm.mod = true; // Add mod flag

      const body = {
        wid: vm.repository.wid,
        id: vm.tag_target[id].id,
        key,
        value,
        delete: delete_id,
      };
      const onError = () => {
        console.log(`[Error] failed to update tag ${body.path}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/tag/update`, body, options)
        .then(
          (resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              vm.tags.splice(id, 1);
              vm.tag_target.splice(id, 1);
            } else {
              onError();
            }
          },
          (error) => {
            onError();
          }
        );
    },
  },
};
</script>

<style>
.ant-select-selection {
  height: 100%;
}
</style>