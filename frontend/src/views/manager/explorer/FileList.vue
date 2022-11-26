<template>
  <div class="file-list" ref="container">
    <!-- File viewer menu -->
    <slot name="file-toolbar"></slot>
    <a-divider />

    <!-- Table -->
    <div class="file-list-table-wrapper">
      <a-table
        tableLayout="fixed"
        :row-selection="{
          columnWidth: 30,
          selectedRowKeys: selectedRowKeys,
          onChange: onSelectChange,
        }"
        :columns="columns"
        :data-source="data"
        :bordered="false"
        :pagination="false"
      >
        <span slot="icon" slot-scope="item">
          <!-- Main dropdown menu -->
          <DropdownMenu
            :trigger="['contextmenu']"
            :item="item"
            @add-tag="addTag"
            @del="del"
            @detail="detail"
            @download="download"
            @goto="goto"
            @moveto="moveto"
            @rename="rename"
          >
            <!-- Image -->
            <div :class='{"file-selected": selected == item.id}'>
              <img
                v-show="item.thumb_done"
                class="list-thumb"
                :key="`${item.fullname}${Math.random()}`"
                :alt="item.fullname"
                :src="item.thumb"
                @load="onLoad(item)"
              />
              <img
                v-if="!item.thumb_done"
                class="list-icon"
                :alt="item.fullname"
                :src="item.icon"
              />
            </div>
          </DropdownMenu>
        </span>

        <span slot="name" slot-scope="item">
          <a-tooltip :title="item.fullname">
            <a @click="goto(item, $event)">{{ item.fullname }}</a>
          </a-tooltip>
        </span>

        <span slot="tags" slot-scope="item">
          <a-tag
            v-for="tag in item.tags"
            :key="`${item.id}${tag.key}:${tag.value}`"
            :color="'geekblue'"
            >{{ `${tag.key}:${tag.value}` }}</a-tag
          >
        </span>

        <span slot="action" slot-scope="item">
          <!-- Secondary dropdown menu -->
          <DropdownMenu
            slot="extra"
            :trigger="['click']"
            :item="item"
            @add-tag="addTag"
            @del="del"
            @detail="detail"
            @download="download"
            @goto="goto"
            @moveto="moveto"
            @rename="rename"
          >
            <a-icon type="down-circle" />
          </DropdownMenu>
        </span>
      </a-table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      columns: [],
      selectedRowKeys: [],
    };
  },
  beforeMount() {
    const vm = this;

    // Table columns
    const columns = [
      {
        title: vm.$i18n.t("all.icon"),
        key: "icon",
        scopedSlots: { customRender: "icon" },
        ellipsis: true,
        width: 100,
        align: "center",
      },
      {
        title: "Name",
        key: "name",
        scopedSlots: { customRender: "name" },
        ellipsis: true,
        align: "left",
      },
      {
        title: "Tags",
        key: "tags",
        scopedSlots: { customRender: "tags" },
        ellipsis: true,
      },
      {
        title: "Size",
        dataIndex: "attr.size",
        ellipsis: true,
      },
      {
        title: "Action",
        key: "action",
        scopedSlots: { customRender: "action" },
        align: "right",
        width: 50,
      },
    ];
    columns.forEach((item) => {
      vm.columns.push(item);
    });
  },
  components: {
    DropdownMenu: () => import("@/components/DropdownMenu.vue"),
  },
  computed: {},
  props: ["data", "selected"],
  methods: {
    addTag(target, event) {
      this.$emit("add-tag", target, event);
    },
    del(target, event) {
      this.$emit("del", target, event);
    },
    detail(target, event) {
      this.$emit("detail", target, event);
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
    onLoad(item) {
      item.thumb_done = true;
    },
    rename(target, event) {
      this.$emit("rename", target, event);
    },
    clearCheck() {
      this.selectedRowKeys = [];
    },
    onChange(e) {
      this.$emit("onChange", e);
    },
    onSelectChange(selectedRowKeys, e) {
      const vm = this;
      vm.selectedRowKeys = selectedRowKeys;

      let checked = [];
      vm.selectedRowKeys.forEach((i) => {
        checked.push(`${vm.data[i].type}-${vm.data[i].id}`);
      });

      // emit
      vm.$emit("check", checked, e);
    },
  },
};
</script>


<style>
.file-list {
  height: 100%;
}

.file-list-table-wrapper {
  height: calc(100% - 38px);
  overflow: auto;
}

.file-list .ant-table-thead > tr:first-child > th:first-child {
  padding: 1px 0;
  width: 60px;
}

.file-list .ant-table-thead > tr > th {
  padding: 5px 0;
}

.list-icon {
  max-height: 80px;
  max-width: 100px;
}

.list-thumb {
  max-height: 80px;
  max-width: 100px;
}
</style>