import json
from subprocess import check_output, PIPE, CalledProcessError

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _


class AvProbeInfo:
    def __init__(
        self, type, format=None, width=None, height=None, duration=None
    ):
        self.type = type
        self.format = format
        self.width = width
        self.height = height
        self.duration = duration


class FileAnalyzer:
    OTHER = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    FORMAT_BINDINGS = {
        'matroska,webm': 'webm',
        'mov,mp4,m4a,3gp,3g2,mj2': 'mp4',
    }
    HTML5_AV_FORMATS = {
        'mp3': (('mp3',),),
        'webm': (('vorbis',), ('vp8', 'vorbis'), ('vp9', 'opus')),
        'ogg': (('vorbis',), ('opus',),
                ('theora', 'vorbis'),),
        'mp4': (('aac',), ('h264', 'mp3'), ('h264', 'aac')),
    }

    def __init__(self, model_instance, field_name):
        self.model_instance = model_instance
        self.field_name = field_name

    @cached_property
    def field(self):
        return self.model_instance._meta.get_field(self.field_name)

    @cached_property
    def file(self):
        return getattr(self.model_instance, self.field_name)

    @cached_property
    def image(self):
        from PIL import Image
        try:
            return Image.open(self.file)
        except OSError:
            return None

    @cached_property
    def image_dimensions(self):
        close = self.file.closed
        self.file.open()
        return get_image_dimensions(self.file, close=close)

    @property
    def image_width(self):
        return self.image_dimensions[0]

    @property
    def image_height(self):
        return self.image_dimensions[1]

    @cached_property
    def avprobe_info(self):
        # Force le fichier à être enregistré pour qu’il puisse être analysé.
        self.field.pre_save(self.model_instance, add=False)

        try:
            for executable in ('avprobe', 'ffprobe'):
                try:
                    stdout = check_output([
                        executable, '-of', 'json',
                        '-show_format', '-show_streams', self.file.path
                    ], stderr=PIPE)
                except:
                    if executable == 'ffprobe':
                        raise
        except CalledProcessError:
            return AvProbeInfo(self.OTHER)

        data = json.loads(stdout.decode())

        format_name = data['format']['format_name']
        if format_name in self.FORMAT_BINDINGS:
            format_name = self.FORMAT_BINDINGS[format_name]
        codecs = tuple(s['codec_name'] for s in data['streams']
                       if 'codec_name' in s)

        if not codecs:
            return AvProbeInfo(self.OTHER)

        width = None
        height = None
        if data['streams'][0]['codec_type'] == 'video':
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']

        if format_name == 'image2':
            assert len(codecs) == 1
            return AvProbeInfo(
                self.IMAGE, codecs[0], width=width, height=height,
            )

        if format_name in self.HTML5_AV_FORMATS \
                and codecs in self.HTML5_AV_FORMATS[format_name]:
            duration = int(float(data['format']['duration']))
            if len(codecs) == 1:
                return AvProbeInfo(self.AUDIO, format_name, duration=duration)
            elif len(codecs) == 2:
                return AvProbeInfo(
                    self.VIDEO, format_name, width=width, height=height,
                    duration=duration,
                )

    @property
    def format_name(self):
        if self.avprobe_info.format is not None:
            return self.avprobe_info.format
        return self.image.format

    @property
    def type(self):
        if self.image_width is not None and self.image_height is not None:
            return self.IMAGE
        if self.avprobe_info.type == self.AUDIO:
            return self.AUDIO
        if self.avprobe_info.type == self.VIDEO:
            return self.VIDEO
        return self.OTHER

    def validate(self, expected_type=None, expected_format=None):
        error = ValidationError(
            _('« %s » n’est pas un fichier valide.')
            % self.field.verbose_name
        )
        if expected_type is not None and self.type != expected_type:
            raise error
        if expected_format is not None and self.format_name != expected_format:
            raise error
