"""Apply the owned BSP patch and execute its mailbox lifecycle with C mocks."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "arm-zena-css/components/safety_island/zephyr/src"
PATCH = ROOT / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch"


def test_reattach_publication_and_fail_closed(tmp_path):
    target = tmp_path / "drivers/ethernet/veth_rpmsg.c"
    target.parent.mkdir(parents=True)
    shutil.copyfile(REFERENCE / "drivers/ethernet/veth_rpmsg.c", target)
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(PATCH)],
                   cwd=tmp_path, check=True, capture_output=True)
    source = target.read_text()
    functions = source[source.index("static int restore_rsc_table("):
                       source.index("void load_rsc_table(")]
    send = source[source.index("int veth_rpmsg_send("):
                  source.index("static int veth_rpmsg_start(")]
    harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stddef.h>
typedef unsigned atomic_val_t;
struct k_work { int unused; };
struct device { void *data; }; struct mbox_msg {};
struct net_pkt {};
struct fw_resource_table { struct { unsigned ver, num; } hdr; unsigned data; };
struct veth_rpmsg_conf { uintptr_t rsc_table_addr, shm_addr; int rsc_table_size, shm_size; };
struct veth_rpmsg_ctx {
    struct k_work notify_work; atomic_val_t pending_events;
    unsigned rpmsg_state; const struct veth_rpmsg_conf *cfg;
    struct { void *vdev; } rvdev;
    int sc_ept;
    struct { int spec; } mbox[7];
};
#define RPMSG_ATTACH 0
#define RPMSG_DETACH 1
#define RPMSG_DETACH_CH_ID 2
#define RPMSG_ATTACH_CH_ID 3
#define RPMSG_ACK_MBX_ID 6
#define VRING1_ID 1
#define BIT(n) (1U << (n))
#define CONTAINER_OF(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define LOG_INF(...) ((void)0)
#define LOG_ERR(...) ((void)0)
static bool rpmsg_ready;
static int veth_link_lock, sent, send_result;
#define K_FOREVER -1
#define K_NO_WAIT 0
#define NET_ETH_MAX_FRAME_SIZE 1500
#define RPMSG_ERR_NO_BUFF -2002
static int k_mutex_lock(int *lock, int wait) {
    if (*lock) return -EBUSY;
    *lock=1; return 0;
}
static void k_mutex_unlock(int *lock) { assert(*lock); *lock=0; }
static size_t net_pkt_get_len(struct net_pkt *pkt) { return 1; }
static int net_pkt_read(struct net_pkt *pkt, void *buf, size_t size) { return 0; }
static int rpmsg_trysend(void *ept, void *buf, size_t size) {
    assert(veth_link_lock && rpmsg_ready); sent++; return send_result;
}
static struct fw_resource_table template = {{1,1}, 42}, shared;
static unsigned char rings[128];
static int size = sizeof(template), seq, destroyed, fenced, acked, setup, notified;
static void rsc_table_get(struct fw_resource_table **p, int *n) { *p=&template; *n=size; }
static void veth_rpmsg_destroy_vdev(struct veth_rpmsg_ctx *c) { destroyed=++seq; }
static int veth_rpmsg_setup_vdev(struct veth_rpmsg_ctx *c) { setup++; return 0; }
static int rproc_virtio_notified(void *v, int id) { notified++; return 0; }
static void barrier_dmem_fence_full(void) { fenced=++seq; }
static int mbox_send_dt(void *p, void *m) {
    assert(shared.hdr.num == 1 && shared.data == 42);
    for (unsigned i=0;i<sizeof(rings);i++) assert(rings[i] == 0);
    assert(fenced > destroyed); acked=++seq; return 0;
}
static unsigned atomic_set(unsigned *p, unsigned n) { unsigned old=*p; *p=n; return old; }
static void atomic_or(unsigned *p, unsigned n) { *p |= n; }
static int k_work_submit(struct k_work *w) { return 0; }
'''
    cases = r'''
int main(void) {
    struct veth_rpmsg_conf cfg = {(uintptr_t)&shared, (uintptr_t)rings, sizeof(shared), sizeof(rings)};
    struct veth_rpmsg_ctx ctx = {.cfg=&cfg, .rpmsg_state=RPMSG_DETACH};
    process_mbox_event(&ctx, RPMSG_ATTACH_CH_ID);
    assert(acked && !destroyed); /* initial attach publishes before ACK */
    ctx.rpmsg_state=RPMSG_ATTACH;
    acked=0; fenced=0; seq=0;
    memset(&shared, 0, sizeof(shared)); /* AP firmware cleared the table */
    memset(rings, 0xff, sizeof(rings));
    platform_mbox_callback(NULL, 0, &ctx, NULL);
    platform_mbox_callback(NULL, RPMSG_ATTACH_CH_ID, &ctx, NULL);
    assert(!destroyed && !acked); /* ISR never frees the vdev. */
    notify_handler(&ctx.notify_work);
    assert(destroyed && acked > fenced && ctx.rpmsg_state == RPMSG_DETACH);
    assert(!notified && !setup); /* discard pre-ACK kicks */
    assert(template.hdr.num == 1 && template.data == 42);
    platform_mbox_callback(NULL, 1, &ctx, NULL);
    notify_handler(&ctx.notify_work);
    assert(setup == 1 && ctx.rpmsg_state == RPMSG_ATTACH);
    platform_mbox_callback(NULL, 1, &ctx, NULL);
    notify_handler(&ctx.notify_work); assert(notified == 1);
    acked=0; size=sizeof(shared)+1;
    process_mbox_event(&ctx, RPMSG_ATTACH_CH_ID);
    assert(!acked && ctx.rpmsg_state == RPMSG_DETACH);
    size=sizeof(shared); template.hdr.num=0;
    process_mbox_event(&ctx, RPMSG_ATTACH_CH_ID); assert(!acked);
    template.hdr.num=1;
    process_mbox_event(&ctx, RPMSG_ATTACH_CH_ID); assert(acked);
    acked=0; process_mbox_event(&ctx, RPMSG_DETACH_CH_ID);
    assert(!acked && setup == 1);
    platform_mbox_callback(NULL, RPMSG_ATTACH_CH_ID, &ctx, NULL);
    platform_mbox_callback(NULL, RPMSG_DETACH_CH_ID, &ctx, NULL);
    notify_handler(&ctx.notify_work); assert(!acked); /* latest lifecycle wins */
    struct device dev={&ctx}; struct net_pkt pkt;
    rpmsg_ready=true; veth_link_lock=1;
    assert(veth_rpmsg_send(&dev, &pkt) == -EAGAIN && !sent);
    veth_link_lock=0; rpmsg_ready=false;
    assert(veth_rpmsg_send(&dev, &pkt) == -EIO && !sent && !veth_link_lock);
    rpmsg_ready=true; send_result=RPMSG_ERR_NO_BUFF;
    assert(veth_rpmsg_send(&dev, &pkt) == -EAGAIN && sent == 1 && !veth_link_lock);
    send_result=0;
    assert(veth_rpmsg_send(&dev, &pkt) == 0 && sent == 2);
    return 0;
}
'''
    unit = tmp_path / "reattach.c"
    unit.write_text(harness + functions + send + cases)
    subprocess.run(["cc", "-std=c11", "-Wall", "-Werror", "-Wno-unused-function",
                    str(unit), "-o", str(tmp_path / "reattach")], check=True)
    subprocess.run([str(tmp_path / "reattach")], check=True, timeout=5)


def test_recipe_uses_generated_qvp_copy():
    recipe = (PATCH.parent.parent / "zephyr-demos-cl1-apollo-common.inc").read_text()
    assert 'APOLLO_SAFETY_ISLAND_MODULE:apollo-qvp = "${WORKDIR}/apollo-safety-island"' in recipe
    assert 'APOLLO_SAFETY_ISLAND_MODULE = "${ZEPHYR_SAFETY_ISLAND_MODULE}"' in recipe
    assert 'apply=no' in recipe
    assert 'addtask prepare_apollo_hipc after do_unpack before do_configure' in recipe
    assert 'd.appendVarFlag("do_prepare_apollo_hipc", "file-checksums", checksums)' in recipe
