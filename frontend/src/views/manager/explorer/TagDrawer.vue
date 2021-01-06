<template>
  <a-drawer
    placement="right"
    :closable="true"
    :maskClosable="true"
    :title="$t('explorer.tag_drawer.title')"
    :visible="visible"
    :after-visible-change="afterVisibleChange"
    @close="onClose"
  >
    <a-select
      mode="multiple"
      v-model="attribute_tag_ids"
      :style="{ width: '100%', height: '200px' }"
      :dropdownMatchSelectWidth="false"
      :placeholder="$t('explorer.tag_drawer.select1_placeholder')"
      :open="show_select"
      @change="select1Change"
    >
      <a-select-option v-for="tag in tags" :key="tag.id" :value="tag.id">{{
        `${tag.key}:${tag.value}`
      }}</a-select-option>
    </a-select>

    <img v-if="target && target.thumb_done" class="image" :alt="target.fullname" :src="target.thumb" @click="show_select=!show_select;" />
    <img v-else class="image" alt="icon" :src="target ? target.icon : null" @click="show_select=!show_select;" />

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
      attribute_tags: [],
      attribute_tag_ids: [],
      tags: [],
      show_select: null,
      mod: false,
      target: null,
      target_id: null,
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
      vm.target = target;

      // load tag
      const body = {
        wid: vm.repository.wid,
      };
      const onError = () => {
        console.log(`[Error] failed to init ${body.path}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/tag/list`, body, options)
        .then(
          (resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              const tag_list = resp.body.data;
              vm.tags.splice(0, vm.tags.length);
              for (let i in tag_list) {
                vm.tags.push(tag_list[i]);
              }
            } else {
              onError();
            }
          },
          (error) => {
            onError();
          }
        );

      // load attribute tag
      vm.attribute_tags.splice(0, vm.attribute_tags.length);
      vm.attribute_tag_ids.splice(0, vm.attribute_tag_ids.length);
      if (target != undefined) {
        vm.target_id = target.type == "dir" ? target.id : target.attribute;
        vm.type = target.type;
        for (let i in target.tags) {
          vm.attribute_tags.push(target.tags[i]);
          vm.attribute_tag_ids.push(target.tags[i].tag_id);
        }
      }
    },
    afterVisibleChange(val) {},
    onClose() {
      const vm = this;
      vm.show_select = false;
      vm.attribute_tags.splice(0, vm.attribute_tags.length);
      vm.$emit("on-close", vm.mod);
    },
    arrDiff(arr1, arr2) {
      for (let i in arr1) {
        if (arr2.indexOf(arr1[i]) < 0) {
          return i;
        }
      }
      return null;
    },
    select1Change(value) {
      const vm = this;

      let tag_ids = [];
      for (let i in vm.attribute_tags)
        tag_ids.push(vm.attribute_tags[i].tag_id);

      if (value.length > vm.attribute_tags.length) {
        // add
        const diff_index = vm.arrDiff(value, tag_ids);
        if (diff_index) vm.addAttributeTag(value[diff_index]);
      } else if (value.length < vm.attribute_tags.length) {
        // delete
        const diff_index = vm.arrDiff(tag_ids, value);
        if (diff_index) vm.updateAttributeTag(diff_index, 1);
      } else {
        // update
        console.log("update select")
      }
      vm.show_select = true;
    },
    btn1Click(e) {
      const vm = this;
      vm.onClose();
    },
    addAttributeTag(tag_id) {
      const vm = this;
      vm.mod = true; // Add mod flag

      const body = {
        wid: vm.repository.wid,
        tag_id,
        target: vm.target_id,
        type: vm.type,
      };
      const onError = () => {
        console.log(`[Error] failed to update tag ${body.path}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/attributetag/add`, body, options)
        .then(
          (resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              // vm.onClose();
              const result = resp.body.data;
              vm.attribute_tags.push(result);
            } else {
              onError();
            }
          },
          (error) => {
            onError();
          }
        );
    },
    updateAttributeTag(index, delete_id) {
      const vm = this;
      vm.mod = true; // Add mod flag

      const body = {
        wid: vm.repository.wid,
        id: vm.attribute_tags[index].id,
        delete: delete_id,
      };
      const onError = () => {
        console.log(`[Error] failed to update tag ${body.path}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/attributetag/update`, body, options)
        .then(
          (resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              vm.attribute_tags.splice(index, 1);
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

.image {
  margin-top: 25px;
  max-height: 500px;
  max-width: 435px;
}
</style>