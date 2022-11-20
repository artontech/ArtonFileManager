<template>
    <a-layout-sider
        v-model="collapsed"
        class="menu"
        width="256"
        breakpoint="lg"
        @collapse="onCollapse"
        @breakpoint="onBreakpoint"
        collapsible
    >
        <a-menu
            :default-selected-keys="[]"
            :default-open-keys="['sub1', 'sub2', 'sub3', 'sub4']"
            :selectedKeys="[selected]"
            mode="inline"
            theme="dark"
            :inline-collapsed="collapsed"
            @openChange="menu1Change"
        >
            <a-menu-item key="Setting" v-on:click="go">
                <a-icon type="setting" />
                <span>{{$t('menu.setting')}}</span>
            </a-menu-item>
            <a-sub-menu key="sub1">
                <span slot="title">
                    <a-icon type="profile" />
                    <span>{{$t('menu.manager')}}</span>
                </span>
                <a-menu-item key="Repository" v-on:click="go">
                    <a-icon type="database" />
                    <span>{{$t('menu.repository')}}</span>
                </a-menu-item>
                <a-menu-item key="Explorer" v-on:click="go">
                    <a-icon type="file" />
                    <span>{{$t('menu.explorer')}}</span>
                </a-menu-item>
                <a-menu-item key="Backup" v-on:click="go">
                    <a-icon type="copy" />
                    <span>{{$t('menu.backup')}}</span>
                </a-menu-item>
                <a-menu-item key="Check" v-on:click="go">
                    <a-icon type="check-circle" />
                    <span>{{$t('menu.check')}}</span>
                </a-menu-item>
            </a-sub-menu>
            <a-sub-menu key="sub2">
                <span slot="title">
                    <a-icon type="cloud" />
                    <span>{{$t('menu.netdisk')}}</span>
                </span>
                <a-sub-menu key="sub3">
                    <span slot="title">
                        <a-icon type="cloud-upload" />
                        <span>{{$t('menu.baidunetdisk')}}</span>
                    </span>
                    <a-menu-item key="BaiduManager" v-on:click="go">
                        <a-icon type="cloud-server" />
                        <span>{{$t('menu.baidumanager')}}</span>
                    </a-menu-item>
                    <a-menu-item key="BaiduSync" v-on:click="go">
                        <a-icon type="cloud-sync" />
                        <span>{{$t('menu.baidusync')}}</span>
                    </a-menu-item>
                    <a-menu-item key="BaiduFix" v-on:click="go">
                        <a-icon type="tool" />
                        <span>{{$t('menu.baidufix')}}</span>
                    </a-menu-item>
                </a-sub-menu>
                <a-sub-menu key="sub4">
                    <span slot="title">
                        <a-icon type="aliyun" />
                        <span>{{$t('menu.oss')}}</span>
                    </span>
                    <a-menu-item key="OssSync" v-on:click="go">
                        <a-icon type="cloud-sync" />
                        <span>{{$t('menu.osssync')}}</span>
                    </a-menu-item>
                </a-sub-menu>
            </a-sub-menu>
        </a-menu>
    </a-layout-sider>
</template>

<script>
export default {
    name: "Menu",
    props: {},
    data() {
        return {
            collapsed: false,
            selected: "",
        };
    },
    created() {
        if (this.$route.name) this.selected = this.$route.name;
        this.$router.beforeResolve((to, from, next) => {
            this.selected = to.name;
            next();
        });
    },
    beforeUpdate() {},
    methods: {
        go(item) {
            this.$router.go(item.key);
        },
        onCollapse(collapsed, type) {
        },
        onBreakpoint(broken) {
        },
        menu1Change() {
        }
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.menu {
    width: 256px;
    height: 100vh;
    background: rgb(0, 12, 23);
}

.menu.collapsed {
    width: fit-content;
}

span > a {
    font-weight: bold;
    color: rgba(255, 255, 255, 0.65);
    height: 40px;
    line-height: 40px;
}
</style>
