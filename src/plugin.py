from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSelection, ConfigInteger, NoSave
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists

f = open("/proc/stb/info/model", "r")
model = ''.join(f.readlines()).strip()

if model in ["one", "two"]:
	config.av.ac3_downmix = NoSave(ConfigSelection(choices = [("downmix",  _("Downmix"))], default = "downmix"))
	config.av.ac3_passthrough = NoSave(ConfigSelection(choices = [("passthrough",  _("Passthrough"))], default = "passthrough"))
	config.av.dts_support = ConfigSelection(choices = [("full",  _("follow AC3")), ("passthrough",  _("Passthrough"))], default = "passthrough")
	config.av.dtshd_support = ConfigSelection(choices = [("full",  _("follow AC3")), ("passthrough",  _("Passthrough")), ("transcode", _("force DTS"))], default = "passthrough")
	config.av.truehd_support = ConfigSelection(choices = [("full",  _("follow AC3")), ("passthrough",  _("Passthrough"))], default = "passthrough")
else:
	config.av.aac = ConfigSelection(choices = [("downmix",  _("Downmix")), ("passthrough", _("Passthrough")), ("multichannel",  _("convert to multi-channel PCM")), ("hdmi_best",  _("use best / controlled by HDMI"))], default = "hdmi_best")
	config.av.ac3 = ConfigSelection(choices = [("downmix",  _("Downmix")), ("passthrough", _("Passthrough")), ("multichannel",  _("convert to multi-channel PCM")), ("hdmi_best",  _("use best / controlled by HDMI"))], default = "hdmi_best")
	config.av.ac3plus = ConfigSelection(choices = [("force_ac3", _("force AC3")), ("force_ddp", _("force AC3+")), ("use_hdmi_caps",  _("controlled by HDMI")), ("multichannel",  _("convert to multi-channel PCM")), ("hdmi_best",  _("use best / controlled by HDMI"))], default = "hdmi_best")
	config.av.wmapro = ConfigSelection(choices = [("downmix",  _("Downmix")), ("passthrough", _("Passthrough")), ("multichannel",  _("convert to multi-channel PCM")), ("hdmi_best",  _("use best / controlled by HDMI"))], default = "hdmi_best")

	if model in ["dm7080","dm820"]:
		config.av.dtshd = ConfigSelection(choices = [("use_hdmi_caps",  _("controlled by HDMI")), ("force_dts", _("force DTS"))], default = "use_hdmi_caps")
	else:
		config.av.dtshd = ConfigSelection(choices = [("downmix",  _("Downmix")), ("force_dts", _("force DTS")), ("use_hdmi_caps",  _("controlled by HDMI")), ("multichannel",  _("convert to multi-channel PCM")), ("hdmi_best",  _("use best / controlled by HDMI"))], default = "hdmi_best")

	if fileExists("/usr/lib/gstreamer-1.0/libgstlibav.so"):
		config.av.truehd = NoSave(ConfigSelection(choices = [("downmix",  _("Downmix"))], default = "downmix"))
	else:
		config.av.truehd = NoSave(ConfigSelection(choices = [("notavail",  _("not available"))], default = "notavail"))

class AudioSetup(Screen, ConfigListScreen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "Setup"
		self.setup_title = _("Advanced Audio Settings")
		self.onChangedEntry = []

		self.list = [ ]
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.keyCancel,
				"save": self.apply,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))

		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("General")))
		self.list.append(getConfigListEntry(_("AC3 default"), config.av.defaultac3))
		self.list.append(getConfigListEntry(_("AC3 downmix"), config.av.downmix_ac3, True))
		self.list.append(getConfigListEntry(_("General AC3 Delay"), config.av.generalAC3delay))
		self.list.append(getConfigListEntry(_("General PCM Delay"), config.av.generalPCMdelay))
		try:
			self.list.append(getConfigListEntry(_("Volume step size (%)"), config.audio.volume_stepsize))
		except:
			pass
		self.list.append(getConfigListEntry(_("Codecs")))
		if model in ["one", "two"]:
			if config.av.downmix_ac3.value:
				self.list.append(getConfigListEntry("Dolby Digital/Dolby Digital Plus/Dolby Atmos", config.av.ac3_downmix))
			else:
				self.list.append(getConfigListEntry("Dolby Digital/Dolby Digital Plus/Dolby Atmos", config.av.ac3_passthrough))
			self.list.append(getConfigListEntry("DTS", config.av.dts_support))
			self.list.append(getConfigListEntry("DTS-HD HR/DTS-HD MA/DTS:X", config.av.dtshd_support))
			self.list.append(getConfigListEntry("Dolby TrueHD/Dolby Atmos", config.av.truehd_support))
		else:
			self.list.append(getConfigListEntry("Dolby Digital", config.av.ac3))
			self.list.append(getConfigListEntry("Dolby Digital Plus/Dolby Atmos", config.av.ac3plus))
			self.list.append(getConfigListEntry("Dolby TrueHD/Dolby Atmos", config.av.truehd))
			self.list.append(getConfigListEntry("DTS/DTS-HD HR/DTS-HD MA/DTS:X", config.av.dtshd))
			self.list.append(getConfigListEntry("AAC/HE-AAC", config.av.aac))
			self.list.append(getConfigListEntry("WMA Pro", config.av.wmapro))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def apply(self):
		self.keySave()

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def _onKeyChange(self):
		try:
			cur = self["config"].getCurrent()
			if cur and cur[2]:
				self.createSetup()
		except:
			pass

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

def InitAudioSwitch():
	if model in ["one", "two"]:
		pass
	else:
		SystemInfo["SupportsAC3PlusTranscode"] = False

		def setAC3Downmix(configElement):
			if not configElement.value:
				open("/proc/stb/audio/ac3", "w").write(config.av.ac3.value)
		config.av.downmix_ac3.addNotifier(setAC3Downmix)

		def setAC3(configElement):
			if not config.av.downmix_ac3.value:
				open("/proc/stb/audio/ac3", "w").write(configElement.value)
		config.av.ac3.addNotifier(setAC3)

		def setDDP(configElement):
			open("/proc/stb/audio/ac3plus", "w").write(configElement.value)
		config.av.ac3plus.addNotifier(setDDP)

		def setDTSHD(configElement):
			open("/proc/stb/audio/dtshd", "w").write(configElement.value)
		config.av.dtshd.addNotifier(setDTSHD)

		def setAAC(configElement):
			open("/proc/stb/audio/aac", "w").write(configElement.value)
		config.av.aac.addNotifier(setAAC)

		def setWMAPRO(configElement):
			open("/proc/stb/audio/wmapro", "w").write(configElement.value)
		config.av.wmapro.addNotifier(setWMAPRO)

def audioSetupMain(session, **kwargs):
	session.open(AudioSetup)

def startSetup(menuid, **kwargs):
	if menuid == "osd_video_audio":
		return [(_("Advanced Audio Settings"), audioSetupMain, "audio_setup", 21)]
	else:
		return []

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Advanced Audio Settings"), description=_("Advanced Audio Settings"), where = PluginDescriptor.WHERE_MENU, needsRestart = False, fnc=startSetup),
		PluginDescriptor(name=_("Audio Settings"), description=_("Audio Settings"), where = PluginDescriptor.WHERE_AUDIOMENU, fnc=audioSetupMain)]

InitAudioSwitch()