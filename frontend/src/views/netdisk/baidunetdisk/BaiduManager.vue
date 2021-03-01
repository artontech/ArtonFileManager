<template>
  <div class="baidumanager">
    <a-row type="flex" justify="space-around" :gutter="[16, 24]">
      <a-col :span="8">
        {{ $t("baidunetdisk.baidumanager.label1_caption") }}
        <a-switch
          :checked="switch1_checked"
          :disabled="switch1_disabled"
          :loading="switch1_loading"
          @change="switch1Change"
        >
          <a-icon slot="checkedChildren" type="check" />
          <a-icon slot="unCheckedChildren" type="close" />
        </a-switch>
      </a-col>
      <a-col :span="6" v-if="switch1_checked">
        <div v-if="baidunetdisk.user_info">
          <a-badge
            dot
            :count="baidunetdisk.user_info.vip_type"
            :title="vipInfo"
          >
            <a-avatar
              shape="square"
              :src="baidunetdisk.user_info.avatar_url"
            /> </a-badge
          >{{ baidunetdisk.user_info.netdisk_name }}({{
            baidunetdisk.user_info.baidu_name
          }})
        </div>
        <a-avatar v-else shape="square" icon="user" />
      </a-col>
      <a-col :span="4" v-else>
        <a-button
          size="small"
          type="primary"
          :disabled="btn1_disabled"
          @click="btn1Click"
          >{{ $t("baidunetdisk.baidumanager.btn1_caption") }}</a-button
        >
      </a-col>
    </a-row>

    <a-row v-if="quota" :gutter="[16, 24]">
      <a-col :span="8">
        <a-card>
          <a-statistic
            title="Total"
            :value="quota.total"
            :precision="2"
            :suffix="quota.total_suffix"
            :value-style="{ color: '#3f8600' }"
            style="margin-right: 50px"
          >
            <template #prefix>
              <a-icon type="pie-chart" />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <a-statistic
            title="Free"
            :value="quota.free"
            :precision="2"
            :suffix="quota.free_suffix"
            :value-style="{ color: '#00aa30' }"
            style="margin-right: 50px"
          >
            <template #prefix>
              <a-icon type="check-square" />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card>
          <a-statistic
            title="Used"
            :value="quota.used"
            :precision="2"
            :suffix="quota.used_suffix"
            class="demo-class"
            :value-style="{ color: '#cf1322' }"
          >
            <template #prefix>
              <a-icon type="container" />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import options from "@/config/request";

export default {
  data() {
    return {
      btn1_disabled: true,
      switch1_checked: false,
      switch1_disabled: false,
      switch1_loading: false,
      quota: null,
    };
  },
  computed: {
    vipInfo() {
      let result = "";
      const user_info = this.baidunetdisk.user_info;
      if (!user_info) return result;
      switch (user_info.vip_type) {
        case 0:
          result = "普通用户";
          break;
        case 1:
          result = "普通会员";
          break;
        case 2:
          result = "超级会员";
          break;
        default:
          break;
      }
      return result;
    },
  },
  beforeMount() {
    const vm = this;
    vm.repository = vm.$store.state.repository;
    vm.setting = vm.$store.state.setting;
    vm.baidunetdisk = vm.$store.state.baidunetdisk;

    if (!vm.repository.wid) vm.$router.go("Repository");
  },
  methods: {
    getUserInfo(info) {
      const vm = this;

      const onError = (e) => {
        console.log(`[Error] failed to get info`, e);
      };
      // Get user info request
      let url = `http://${vm.setting.address}/baidunetdisk/userinfo?access_token=${info.access_token}`;
      vm.$http.get(url).then(
        (resp) => {
          if (resp.body.status === "success") {
            vm.$store.commit("updateBaiduNetdisk", {
              user_info: resp.body.data,
            });
          } else {
            onError(resp.body);
          }
        },
        (error) => {
          onError(error);
        }
      );

      // Get quota request
      function parseMemory(quota, item) {
        const suffix_list = ["KB", "MB", "GB", "TB", "PB"];
        let mem = quota[item];
        let suffix = "Byte";
        for (let i in suffix_list) {
          if (mem < 1024) break;
          mem /= 1024.0;
          suffix = suffix_list[i];
        }

        quota[item] = mem;
        quota[item + "_suffix"] = suffix;
      }
      url = `http://${vm.setting.address}/baidunetdisk/quota?access_token=${info.access_token}`;
      vm.$http.get(url).then(
        (resp) => {
          if (resp.body.status === "success") {
            const quota = resp.body.data;
            parseMemory(quota, "total");
            parseMemory(quota, "free");
            parseMemory(quota, "used");
            vm.quota = quota;
          } else {
            onError(resp.body);
          }
        },
        (error) => {
          onError(error);
        }
      );
    },
    /* * * * * * * * Start: Trigger * * * * * * * */
    switch1Change(checked, event) {
      const vm = this;
      const body = {
        wid: vm.repository.wid,
      };
      vm.switch1_checked = checked;
      vm.switch1_loading = true;
      const onError = () => {
        console.log(`[Error] failed to get baidu token ${body.path}`);
        vm.btn1_disabled = false;
        vm.switch1_loading = false;
        vm.switch1_checked = !checked;
      };
      vm.$http
        .post(`http://${vm.setting.address}/baidunetdisk/token`, body, options)
        .then((resp) => {
          vm.switch1_loading = false;
          if (resp.body.status === "success") {
            vm.switch1_disabled = true;
            vm.$store.commit("updateBaiduNetdiskNocache", {
              info: resp.body.data,
            });
            vm.getUserInfo(resp.body.data);
          } else {
            if (resp.body.err === "token_expire") {
              vm.$store.commit("updateBaiduNetdiskNocache", {
                info: resp.body.data,
              });
              vm.btn1_disabled = false;
              vm.switch1_loading = false;
              vm.switch1_checked = !checked;
            } else if (checked) {
              // Failed to open
              vm.switch1_checked = false;
              onError(resp.body.err);
            }
          }
        }, onError);
    },
    btn1Click(event) {
      const vm = this;
      window.open(
        "http://openapi.baidu.com/oauth/2.0/authorize?" +
          `response_type=code&client_id=${vm.baidunetdisk.nocache.info.api_key}&` +
          `redirect_uri=http://${vm.setting.address}/baidunetdisk/oauth&scope=basic,netdisk&` +
          "display=page&qrcode=1&confirm_login=1&state=" +
          vm.repository.wid
      );
      vm.btn1_disabled = true;
    },
    /* * * * * * * * End: Trigger * * * * * * * */
  },
};
</script>

<style>
</style>