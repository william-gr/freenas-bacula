from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from baculaUI import choices


class BaculaSDService(models.Model):
    enable = models.BooleanField(default=False)

class BaculaSDStorage(models.Model):
    """
    Django model describing every tunable setting for bacula
    """

    baculasd_st_name = models.CharField(
            default="freenas-sd",
            help_text=_("Specifies the Name of the Storage daemon. This "
                "directive is required."),
            max_length=255,
            unique=True,
            verbose_name=_("Name"),
            )
    baculasd_st_sdport = models.IntegerField(
            default=9103,
            help_text=_("Maximum number of Jobs that may run concurrently."),
            unique=True,
            validators=[MinValueValidator(1), MaxValueValidator(65535)],
            verbose_name=_("Port"),
            )
    baculasd_st_maximumconcurrentjobs = models.IntegerField(
            default=10,
            help_text=_("Maximum number of Jobs that may run concurrently."),
            verbose_name=_("Maximum Concurrent Jobs"),
            )
    baculasd_st_proceeddespiteioerrors = models.BooleanField(
            default=False,
            help_text=_("Proceed despite I/O errors."),
            verbose_name=_("Proceed despite I/O errors"),
            )

    def __unicode__(self):
        return self.baculasd_st_name

    class Meta:
        verbose_name = _("Storage Daemon")
        verbose_name_plural = _("Storage Daemons")


class BaculaSDDirector(models.Model):
    baculasd_dir_name = models.CharField(
            default="bacula-dir",
            help_text=_("Specifies the Name of the Director allowed to connect"
                "  to the Storage daemon. This directive is required."),
            max_length=255,
            unique=True,
            verbose_name=_("Name"),
            )
    baculasd_dir_password = models.CharField(
            default="",
            help_text=_("Specifies the password that must be supplied by the "
                "above named Director. This directive is required."),
            max_length=255,
            verbose_name=_("Password"),
            )
    baculasd_dir_monitor = models.BooleanField(
            default=False,
            help_text=_("If Monitor is set to no (default), this director "
                "will have full access to this Storage daemon. If Monitor is "
                "set to yes, this director will only be able to fetch the "
                "current status of this Storage daemon."),
            verbose_name=_("Monitor"),
            )

    def __unicode__(self):
        return self.baculasd_dir_name

    class Meta:
        verbose_name = _("Director")
        verbose_name_plural = _("Directors")


class BaculaSDDevice(models.Model):
    baculasd_dev_name = models.CharField(
            default="FileStorage",
            help_text=_("Specifies the Name that the Director will use when "
                "asking to backup or restore to or from to this device."),
            max_length=127,
            unique=True,
            verbose_name=_("Name"),
            )
    baculasd_dev_mediatype = models.CharField(
            choices=choices.BACULASD_DEV_MEDIATYPE_CHOICES,
            default="File",
            help_text=_("The Media Type specification allows you to explicitly"
                " tell Bacula what kind of device you are defining."),
            max_length=5,
            verbose_name=_("Media Type"),
            )
    baculasd_dev_archivedevice = models.CharField(
            default="/mnt/tank/bacula",
            help_text=_("The specified name-string gives the system file name"
                " of the storage device managed by this storage daemon."),
            max_length=255,
            unique=True,
            verbose_name=_("Archive Device"),
            )
    baculasd_dev_labelmedia = models.BooleanField(
            default=True,
            help_text=_("If Yes, permits this device to automatically label "
                "blank media without an explicit operator command."),
            verbose_name=_("Label Media"),
            )
    baculasd_dev_randomaccess = models.BooleanField(
            default=True,
            help_text=_("If Yes, the archive device is assumed to be a random"
                " access medium which supports the lseek (or lseek64 if "
                "Largefile is enabled during configuration) facility."),
            verbose_name=_("Random access"),
            )
    baculasd_dev_removablemedia = models.BooleanField(
            default=False,
            help_text=_("If Yes, this device supports removable media (for "
                "example, tapes or CDs). If No, media cannot be removed (for "
                "example, an intermediate backup area on a hard disk)."),
            verbose_name=_("Removable media"),
            )
    baculasd_dev_alwaysopen = models.BooleanField(
            default=False,
            help_text=_("If Yes (default), Bacula will always keep the device"
                "open unless specifically unmounted by the Console program."),
            verbose_name=_("Always open"),
            )
    baculasd_dev_maximumconcurrentjobs = models.IntegerField(
            blank=True,
            default=0,
            help_text=_("Maximum number of Jobs that can run concurrently on "
                "this Device."),
            verbose_name=_("Maximum Concurrent Jobs"),
            )

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")

    def __unicode__(self):
        return unicode(self.baculasd_dev_name)


class BaculaSDMessages(models.Model):
    baculasd_msg_name = models.CharField(
            default="Standard",
            help_text=_("The name of the Messages resource."),
            max_length=255,
            unique=True,
            verbose_name=_("Name"),
            )
    baculasd_msg_destination = models.CharField(
            choices=choices.BACULASD_MSG_DESTINATION_CHOICES,
            default="director",
            help_text=_("The destinations to which messages should be sent."),
            max_length=15,
            verbose_name=_("Destination"),
            )
    baculasd_msg_address = models.CharField(
            blank=True,
            default="bacula-dir",
            help_text=_("The destinations address."),
            max_length=255,
            verbose_name=_("Address"),
            )
    baculasd_msg_msgtype1 = models.CharField(
            choices=choices.BACULASD_MSG_MSGTYPE_CHOICES,
            default="all",
            max_length=9,
            verbose_name=_("Message Type 1"),
            )
    baculasd_msg_msgtype2 = models.CharField(
            blank=True,
            choices=choices.BACULASD_MSG_MSGTYPE_CHOICES,
            default="",
            max_length=9,
            verbose_name=_("Message Type 2"),
            )
    baculasd_msg_msgtype3 = models.CharField(
            blank=True,
            choices=choices.BACULASD_MSG_MSGTYPE_CHOICES,
            default="",
            max_length=9,
            verbose_name=_("Message Type 3"),
            )
    baculasd_msg_msgtypeaux = models.TextField(
            blank=True,
            default="# message-type4, message-type5, message-type6, ... ",
            help_text=_("Comma separated list of additional message types."),
            verbose_name=_("Auxiliary message types"),
            )

    class Meta:
        verbose_name = _("Messages")
        verbose_name_plural = _("Messages")

    def __unicode__(self):
        return unicode(self.baculasd_msg_name)


class BaculaSDDeviceAssignment(models.Model):
    baculasd_map_device = models.ForeignKey(
            BaculaSDDevice,
            verbose_name=_("Device resource"),
            )
    baculasd_map_storage = models.ForeignKey(
            BaculaSDStorage,
            verbose_name=_("Storage Daemon"),
            )

    class Meta:
        verbose_name = _("Device assignment")
        verbose_name_plural = _("Device assignments")

    def __unicode__(self):
        return u"%s -> %s" % (
            unicode(self.baculasd_map_device),
            unicode(self.baculasd_map_storage),
            )


class BaculaSDDirectorAssignment(models.Model):
    baculasd_map_director = models.ForeignKey(
            BaculaSDDirector,
            verbose_name=_("Director resource"),
            )
    baculasd_map_storage = models.ForeignKey(
            BaculaSDStorage,
            verbose_name=_("Storage Daemon"),
            )

    class Meta:
        verbose_name = _("Director assignment")
        verbose_name_plural = _("Director assignments")

    class FreeAdmin:
        icon_model = u"BaculaDirectorMapIcon"
        icon_object = u"BaculaDirectorMapIcon"
        menu_child_of = "BaculaSD"

    def __unicode__(self):
        return u"%s -> %s" % (
            unicode(self.baculasd_map_director),
            unicode(self.baculasd_map_storage),
            )


class BaculaSDMessagesAssignment(models.Model):
    baculasd_map_messages = models.ForeignKey(
            BaculaSDMessages,
            verbose_name=_("Messages resource"),
            )
    baculasd_map_storage = models.ForeignKey(
            BaculaSDStorage,
            verbose_name=_("Storage Daemon"),
            )

    class Meta:
        verbose_name = _("Messages assignment")
        verbose_name_plural = _("Messages assignments")

    def __unicode__(self):
        return u"%s -> %s" % (
            unicode(self.baculasd_map_messages),
            unicode(self.baculasd_map_storage),
            )
