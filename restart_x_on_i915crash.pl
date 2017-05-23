#! /usr/bin/perl
#
# This is a very simple script that monitors kernel logs using 
# journalctl in order to find crashes.  Then search for i915 ones.
# If found, restart the X services in place.
#
# Run it via crontab every 5 minutes as root.

use strict;

my $DELTATIME = 5;         # in minutes - must be the same in crontab
my $GRAPHSERVICE = "sddm"; # the graphical server you're running
my $logcmd = "journalctl -k --since \"$DELTATIME minutes ago\"";
my $now = localtime();

open(CMD, "$logcmd|") or die "Impossible to run such command: $!\n";

my $crash_flag = 0;
foreach my $line (<CMD>) {
    # crash looks likes this
    #  [41395.831160] RIP: 0010:gen8_ppgtt_alloc_page_directories.isra.39+0x124/0x290 [i915]
    if ($line =~ m/ RIP: .* \[i915\]/) {
        $crash_flag++;
    }
}

if ($crash_flag > 0) {
    print "[ $now ] Crash detected.  Restarting $GRAPHSERVICE\n";
    system("systemctl -f stop $GRAPHSERVICE");
    print "[ $now ] Stop done.\n";
    system("systemctl start $GRAPHSERVICE");
    print "[ $now ] Start done.\n";
} else {
 print "[ $now ] system is ok\n";
}

"
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829850] BUG: unable to handle kernel NULL pointer dereference at 0000000000000018
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829922] IP: gen8_ppgtt_alloc_page_directories.isra.39+0x124/0x290 [i915]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829957] PGD 0 
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829958] 
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829979] Oops: 0002 [#1] PREEMPT SMP
May 17 20:03:40 elxaf7qtt32 kernel: [41395.829999] Modules linked in: psmouse usbhid snd_usb_audio snd_usbmidi_lib cpuid cmac ctr ccm nvram msr pci_stub vboxpci(OE) vboxnetadp(OE) vboxnetflt(OE) vboxdrv(OE) xfrm_user xfrm_algo br_netfilter xt_CHECKSUM iptable_mangle ipt_MASQUERADE nf_nat_masquerade_ipv4 iptable_nat overlay nf_nat_ipv4 bridge stp llc ebtable_filter ebtables rfcomm bnep uvcvideo videobuf2_vmalloc btusb videobuf2_memops btrtl videobuf2_v4l2 btbcm btintel videobuf2_core bluetooth videodev media cdc_ether usbnet r8152 mii binfmt_misc dell_wmi dell_laptop dell_smbios dcdbas arc4 iwlmvm mac80211 intel_rapl intel_powerclamp coretemp iwlwifi snd_hda_codec_hdmi rtsx_pci_ms cfg80211 memstick snd_hda_codec_realtek joydev input_leds snd_hda_codec_generic serio_raw snd_soc_rt286 snd_soc_ssm4567 snd_soc_rl6347a snd_soc_core elan_i2c
May 17 20:03:40 elxaf7qtt32 kernel: [41395.830370]  snd_compress ac97_bus snd_hda_intel snd_seq_midi snd_pcm_dmaengine snd_seq_midi_event snd_hda_codec snd_rawmidi snd_hda_core snd_seq intel_pch_thermal snd_hwdep snd_pcm snd_seq_device lpc_ich mei_me shpchp snd_timer mei snd soundcore wmi intel_vbtn soc_button_array int3403_thermal intel_hid sparse_keymap snd_soc_sst_acpi dw_dmac snd_soc_sst_match i2c_designware_platform processor_thermal_device int3400_thermal acpi_pad intel_soc_dts_iosf acpi_thermal_rel acpi_als int3402_thermal i2c_designware_core spi_pxa2xx_platform 8250_dw int340x_thermal_zone tpm_crb kfifo_buf intel_smartconnect mac_hid industrialio kvm_intel ip6t_REJECT nf_reject_ipv6 kvm nf_log_ipv6 irqbypass xt_hl ip6t_rt nf_conntrack_ipv6 nf_defrag_ipv6 ipt_REJECT nf_reject_ipv4 nf_log_ipv4 nf_log_common xt_LOG xt_limit xt_tcpudp
May 17 20:03:40 elxaf7qtt32 kernel: [41395.830727]  xt_addrtype nf_conntrack_ipv4 nf_defrag_ipv4 xt_conntrack ip6table_filter ip6_tables nf_conntrack_netbios_ns nf_conntrack_broadcast nf_nat_ftp nf_nat nf_conntrack_ftp nf_conntrack libcrc32c iptable_filter parport_pc ip_tables ppdev x_tables lp parport autofs4 btrfs xor raid6_pq algif_skcipher af_alg dm_crypt hid_generic hid mmc_block crct10dif_pclmul crc32_pclmul ghash_clmulni_intel pcbc rtsx_pci_sdmmc i915 aesni_intel i2c_algo_bit aes_x86_64 drm_kms_helper crypto_simd glue_helper syscopyarea cryptd sysfillrect sysimgblt fb_sys_fops ahci rtsx_pci drm libahci video sdhci_acpi sdhci [last unloaded: usbhid]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831006] CPU: 1 PID: 8174 Comm: chromium-browse Tainted: G           OE   4.11.1-helio #4
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831047] Hardware name: Dell Inc. XPS 13 9343/0F5KF3, BIOS A03 03/25/2015
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831091] task: ffff998ccd319d00 task.stack: ffffa2fd43150000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831160] RIP: 0010:gen8_ppgtt_alloc_page_directories.isra.39+0x124/0x290 [i915]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831196] RSP: 0018:ffffa2fd431538b0 EFLAGS: 00010286
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831222] RAX: ffff998c43974700 RBX: 0000000000000003 RCX: 0000000000000003
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831266] RDX: 0000000000000000 RSI: ffff998c5be90000 RDI: 00000000ffffffff
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831310] RBP: ffffa2fd43153910 R08: 0000000000000018 R09: 0000000000000000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831343] R10: 0000000000000000 R11: 0000000000000000 R12: ffff998c8b448000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831396] R13: ffff998c703457b0 R14: 00000000fffe7000 R15: 0000000000008000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831430] FS:  00007f660c42ca40(0000) GS:ffff998d5e480000(0000) knlGS:0000000000000000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831467] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831495] CR2: 0000000000000018 CR3: 0000000213f3f000 CR4: 00000000003406a0
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831549] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831582] DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831625] Call Trace:
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831668]  gen8_alloc_va_range_3lvl+0xc8/0x970 [i915]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831697]  ? finish_task_switch+0x83/0x230
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831730]  ? add_hole+0xfd/0x120 [drm]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831767]  gen8_alloc_va_range+0x273/0x440 [i915]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831809]  i915_vma_bind+0x85/0x210 [i915]
May 17 20:03:40 elxaf7qtt32 kernel: [41395.831848]  __i915_vma_do_pin+0x397/0x600 [i915]
"
