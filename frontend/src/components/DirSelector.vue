<template>
  <a-modal
    v-model="modal1_visible"
    :title="$t('explorer.dir_selector.title')"
    :ok-text="$t('all.ok')"
    :cancel-text="$t('all.cancel')"
    @ok="modal1OK"
  >
    <div class="selector">
      <a-tree
        :load-data="tree1LoadData"
        :expanded-keys="tree1_expanded_keys"
        :loadedKeys="tree1_loaded_keys"
        :tree-data="tree1_data"
        @expand="tree1Expand"
        @select="tree1Select"
      />
    </div>
  </a-modal>
</template>

<script>
import options from "@/config/request";

export default {
  name: "DirSelector",
  props: {},
  data() {
    return {
      repository: null,
      setting: null,
      tree1_data: [
        { title: this.$i18n.t("all.root_dir"), key: "0", isLeaf: false }
      ],
      tree1_expanded_keys: [],
      tree1_loaded_keys: [],
      tree1_selected_keys: [],
      modal1_visible: false,
      mode: "",
      target: undefined
    };
  },
  created() {},
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;
  },
  methods: {
    initShow(mode, target) {
      const vm = this;
      vm.tree1_data.length = 0;
      vm.tree1_data.push({
        title: vm.$i18n.t("all.root_dir"),
        key: "0",
        isLeaf: false
      });
      vm.tree1_expanded_keys.length = 0;
      vm.tree1_loaded_keys.length = 0;
      vm.tree1_selected_keys.length = 0;
      vm.mode = mode;
      vm.target = target;
      vm.modal1Show();
    },
    tree1LoadData(treeNode) {
      const vm = this;
      return new Promise(resolve => {
        if (treeNode.dataRef.children) {
          resolve();
          return;
        }
        treeNode.dataRef.children = [];

        // Sending request
        const body = {
          wid: vm.repository.wid,
          current: Number(treeNode.eventKey),
          thumb: false,
          dir: true,
          file: false
        };
        const onError = () => {
          console.log(`[Error] failed to list dir ${body.current}`);
          resolve();
        };
        vm.$http
          .post(`http://${vm.setting.address}/dir/list`, body, options)
          .then(
            resp => {
              const data = resp.body?.data;
              if (data && resp.body?.status === "success") {
                data.list?.forEach(obj => {
                  if (obj.delete || obj.type != "dir") return;
                  treeNode.dataRef.children.push({
                    title: `${obj.name}`,
                    key: `${obj.id}`
                  });
                });
                vm.tree1_data = [...vm.tree1_data];
                vm.tree1_loaded_keys.push(treeNode.eventKey);
                resolve();
              } else {
                onError();
              }
            },
            error => {
              onError();
            }
          );
      });
    },
    tree1Expand(expandedKeys) {
      this.tree1_expanded_keys = expandedKeys;
    },
    tree1Select(selectedKeys, info) {
      const vm = this;
      vm.tree1_selected_keys = selectedKeys;
    },
    modal1Show() {
      const vm = this;
      vm.modal1_visible = true;
    },
    modal1OK() {
      const vm = this;
      vm.$emit("ok", vm.mode, vm.target, vm.tree1_selected_keys);
      vm.modal1_visible = false;
    }
  }
};
</script>

<style scoped>
.selector {
  max-height: calc(100vh - 300px);
  overflow: auto;
}
</style>