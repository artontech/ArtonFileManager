<template>
  <a-drawer
    placement="right"
    width="80%"
    :closable="true"
    :maskClosable="true"
    :title="$t('explorer.tag_drawer.title')"
    :visible="visible"
    :after-visible-change="afterVisibleChange"
    @close="onClose"
  >
    <div class="select-wrapper">
      <a-select
        mode="multiple"
        v-model="attribute_tag_ids"
        :style="{ width: '100%' }"
        :dropdownMatchSelectWidth="false"
        :placeholder="$t('explorer.tag_drawer.select1_placeholder')"
        :open="show_select"
        @change="select1Change"
      >
        <a-select-option v-for="tag in tags" :key="tag.id" :value="tag.id">{{
          `${tag.key}:${tag.value}`
        }}</a-select-option>
      </a-select>
    </div>

    <PicViewer
      ref="picViewer"
      v-if="target && target.thumb_done"
      id="pic-viewer"
      class="pic-viewer"
      :alt="target.fullname"
      :src="target.thumb"
      @click="show_select=!show_select;" 
    />
    <a-dropdown v-else class="drop-down" :disabled="downloading">
      <a-menu slot="overlay" @click="menu1Click">
        <a-menu-item key="download_baidu">
          {{$t("explorer.tag_drawer.download_baidu")}}
        </a-menu-item>
        <a-menu-item key="download_oss">
          {{$t("explorer.tag_drawer.download_oss")}}
        </a-menu-item>
      </a-menu>
      <a-button> {{$t("all.download")}} <a-icon type="down" /> </a-button>
    </a-dropdown>
  </a-drawer>
</template>

<script>
import options from "@/config/request";
import PicViewer from "./PicViewer";

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
      downloading: false,
    };
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;

    if (!vm.repository.wid) {
      return;
    }
    
    vm.init();
  },
  components: {
    PicViewer,
  },
  computed: {
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
    afterVisibleChange(visible) {
      const vm = this;
      if (visible) {
        vm.$nextTick(() => {
          vm.$refs.picViewer?.init();
        });
      } else {
        vm.$refs.picViewer?.onClose();
      }
    },
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
    menu1Click(e) {
      const vm = this;
      vm.downloading = true;

      const body = {
        wid: vm.repository.wid,
        attribute: vm.target.attribute,
      };
      const onError = () => {
        vm.downloading = false;
        console.log(`[Error] failed to download ${body.path}`);
        vm.$message.error(vm.$i18n.t("explorer.tag_drawer.download_fail"));
      };
      switch (e.key) {
        case "download_baidu":
          vm.$http
          .post(`http://${vm.setting.address}/baidunetdisk/download`, body, options)
          .then(
            (resp) => {
              if (resp.body.status === "success") {
                vm.downloading = false;
                vm.mod = true;
                vm.onClose();
              } else {
                onError();
              }
            },
            (error) => {
              onError(error);
            }
          );
          break;
      }
    },
  },
};
</script>

<style>
.ant-drawer > .ant-drawer-content-wrapper {
  min-width: 200px;
}

.ant-drawer-body {
  padding: 15px;
}

.ant-select-selection {
  height: 100%;
}

.pic-viewer {
  margin-top: 15px;
  height: calc(100vh - 200px);
  width: 100%;
}

.drop-down {
  margin-top: 15px;
}

.select-wrapper {
  width: 100%;
  max-height: 60px;
  overflow: auto;
}
</style>