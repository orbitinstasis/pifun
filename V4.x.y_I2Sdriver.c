#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kmod.h>
#include <linux/platform_device.h>
#include <sound/simple_card.h>
#include <linux/delay.h>

/*
modified by B Kazemi for linux 4.x.y

inspired by https://github.com/msperl/spi-config
with thanks for https://github.com/notro/rpi-source/wiki

to use a differant (simple-card compatible) codec
change the codec name string in two places and the
codec_dai name string. (see codec's source file)

playback vs capture is determined by the codec choice
*/

void device_release_callback(struct device *dev) { /* do nothing */ };

static struct asoc_simple_card_info snd_rpi_simple_card_info = {
	.card = "snd_rpi_simple_card", // -> snd_soc_card.name
	.name = "simple-card_codec_link", // -> snd_soc_dai_link.name
	.codec = "snd-soc-dummy", // "dmic-codec", // -> snd_soc_dai_link.codec_name

	// cat /sys/kernel/debug/asoc should show you which i2s platform to use
	.platform = "3f203000.i2s",//"bcm2708-i2s.0",//"bcm2708-i2s.0", // -> snd_soc_dai_link.platform_name 
	.daifmt = SND_SOC_DAIFMT_I2S | SND_SOC_DAIFMT_NB_NF | SND_SOC_DAIFMT_CBM_CFM, 
	/*	Above flags correspond to (respectively):
			I2S mode, normal bit clock + frame, codec clk & FRM master
	*/
	.cpu_dai = {
		.name = "3f203000.i2s",//"bcm2708-i2s.0",//"bcm2708-i2s.0", // -> snd_soc_dai_link.cpu_dai_name
		.sysclk = 0 
	},
	.codec_dai = {
		.name = "snd-soc-dummy-dai", //"dmic-codec", // -> snd_soc_dai_link.codec_dai_name
		.sysclk = 0 
	},
};

static struct platform_device snd_rpi_simple_card_device = {
	.name = "asoc-simple-card", //module alias
	.id = 0,
	.num_resources = 0,
	.dev = { 
		.release = &device_release_callback,
		.platform_data = &snd_rpi_simple_card_info, // this is a hack
	},
};

// static struct platform_device snd_rpi_codec_device = {
// 	.name = "snd-soc-dummy", // "dmic-codec", //module alias
// 	.id = -1,
// 	.num_resources = 0,
// 	.dev = { .release = &device_release_callback,
// 		},
// };

int i2s_card_init(void) {
	const char *dmaengine = "bcm2708-dmaengine"; //module name
	int ret;

	ret = request_module(dmaengine);
	pr_alert("request module load '%s': %d\n",dmaengine, ret);

	//	ret = platform_device_register(&snd_rpi_codec_device);
	//	pr_alert("register platform device '%s': %d\n",snd_rpi_codec_device.name, ret);

	ret = platform_device_register(&snd_rpi_simple_card_device);
	pr_alert("register platform device '%s': %d\n",snd_rpi_simple_card_device.name, ret);

	pr_alert("Mounted the I2S sound card, arecord -l should show it as a capture device.\n");
	return 0;
}

void i2s_card_exit(void) {
	// you'll have to sudo modprobe -r the card & codec drivers manually (first?)
	// platform_device_unregister(&snd_rpi_simple_card_device);
	platform_device_unregister(&snd_rpi_simple_card_device);
	// pr_alert("Goodbye World!\n");
	pr_alert("Dismounting the I2S sound card.\n");
}

module_init(i2s_card_init);
module_exit(i2s_card_exit);
MODULE_DESCRIPTION("ASoC simple-card I2S setup");
MODULE_AUTHOR("Plugh Plover. Edited for Raspian 4.1.y by B Kazemi");
MODULE_LICENSE("GPL v2");
